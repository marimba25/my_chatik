"""
Функции ​к​лиента:​
- сформировать ​​presence-сообщение;
- отправить ​с​ообщение ​с​ерверу;
- получить ​​ответ ​с​ервера;
- разобрать ​с​ообщение ​с​ервера;
- параметры ​к​омандной ​с​троки ​с​крипта ​c​lient.py ​​<addr> ​[​<port>]:
- addr ​-​ ​i​p-адрес ​с​ервера;
- port ​-​ ​t​cp-порт ​​на ​с​ервере, ​​по ​у​молчанию ​​7777.
"""
import sys
import logging
import time
from socket import socket, AF_INET, SOCK_STREAM
import log.client_log_config
from log.decorators import Log
from jim.protocol import JimMessage, JimResponse
from jim.config import *
from client_errors import WrongModeError
from repo.client_repo import DbRepo
from repo.client_models import Base
import threading
from queue import Queue
from jim.errors import MandatoryKeyError

# Получаем по имени клиентский логгер, он уже нестроен в log_config
logger = logging.getLogger('client')
# создаем класс декоратор для логирования функций
log = Log(logger)


# тот клиент, с которым я общаюсь
class Client:
    """Клиент"""

    def __init__(self, name, addr='localhost', port=7777):
        """
        :param addr: адрес
        :param port: порт
        """
        self.name = name
        self.addr = addr
        self.port = port
        # Создаем клиенский репозиторий
        self.repo = DbRepo('{}.db'.format(self.name), Base)
        # Создаем очередь для обработки ответов от сервера
        self.request_queue = Queue()

    @log
    def connect(self):
        """
        Подключение к серверу
        """
        # Создать сокет TCP
        s = socket(AF_INET, SOCK_STREAM)
        # Соединиться с сервером
        s.connect((self.addr, self.port))
        # Сохраняем сокет
        self.socket = s
        # При соединении сразу отправляем сообщение о присутствии
        self.send_presence()

    def disconnect(self):
        # Отключаемся
        self.socket.close()

    def send_presence(self):
        """Отправить сообщение о присутствии"""
        presence_msg = JimMessage(action=PRESENCE, time=time.time(), user={ACCOUNT_NAME: self.name})
        # переводим в байты и отправляем
        self.socket.sendall(bytes(presence_msg))

        # получаем ответ в байтах
        presence_response_bytes = self.socket.recv(1024)
        # создаем ответ из байт
        presence_response = JimResponse.create_from_bytes(presence_response_bytes)
        return presence_response

    def get_contacts(self):
        """Получить список контактов"""
        # формируем сообщение
        list_message = JimMessage(action=GET_CONTACTS, time=time.time(), user=self.name)
        # отправляем
        self.socket.sendall(bytes(list_message))
        # дальше слушатель получит ответ, который мы получим из очереди
        jm = self.request_queue.get()
        if jm.response == ACCEPTED:
            # получаем следующее сообщение из очереди, там должен быть список контактов
            jm = self.request_queue.get()
            contact_list = jm.action
            # обновим контакты в базе
            self.repo.clear_contacts()
            for contact in contact_list:
                self.repo.add_contact(contact)
            self.repo.commit()
            return contact_list

    def add_contact(self, username):
        # формируем сообщение на добавления контакта
        add_message = JimMessage(action=ADD_CONTACT, user_id=username, time=time.time(), user=self.name)
        # отправляем сообщение на сервер
        self.socket.sendall(bytes(add_message))
        # получаем ответ от сервера
        # ответ получает слушатель, мы его получаем через очередь
        jm = self.request_queue.get()
        if jm.response == OK:
            # Добавляем в свою базу контактов
            self.repo.add_contact(username)
            self.repo.commit()

    def del_contact(self, username):
        # формируем сообщение на добавления контакта
        message = JimMessage(action=DEL_CONTACT, user_id=username, time=time.time(), user=self.name)
        # отправляем сообщение на сервер
        self.socket.sendall(bytes(message))
        # получаем ответ от сервера
        # получаем ответ из очереди
        # Формируем сообщение из байт
        jm = self.request_queue.get()
        if jm.response == OK:
            print('Контакт {} успешно удален'.format(username))
            # удаляем контакт из своей базы
            self.repo.del_contact(username)
            self.repo.commit()

    def add_my_avatar(self, avatar_data):
        self.repo.add_my_avatar(avatar_data=avatar_data)
        self.repo.commit()

        # формируем сообщение
        add_avatar_message = JimMessage(action=ADD_AVATAR, time=time.time(), user=self.name,
                                        avatar_data=JimMessage.bytes_to_base64str(avatar_data))

        # отправляем
        self.socket.sendall(bytes(add_avatar_message))


    def get_my_avatar(self):
        return self.repo.get_my_avatar()

    def get_avatar_for_username(self, username):
        """Получить аватар с сервера"""
        # формируем сообщение
        get_avatar_message = JimMessage(action=GET_AVATAR, time=time.time(), user=username)
        # отправляем
        self.socket.sendall(bytes(get_avatar_message))
        # дальше слушатель получит ответ, который мы получим из очереди
        jm = self.request_queue.get()
        if jm.response == ACCEPTED:
            # получаем следующее сообщение из очереди, там должен быть список контактов
            jm = self.request_queue.get()
            return JimMessage.base64str_to_bytes(jm.action)

    def get_my_avatar_from_server(self):
        return self.get_avatar_for_username(self.name)

    def send_message(self, to, text):
        # формируем сообщение
        message = JimMessage(**{ACTION: MSG, TO: to, FROM: self.name, MESSAGE: text, TIME: time.time()})
        # отправляем
        self.socket.sendall(bytes(message))
