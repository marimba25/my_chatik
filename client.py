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

# Получаем по имени клиентский логгер, он уже нестроен в log_config
logger = logging.getLogger('client')
# создаем класс декоратор для логирования функций
log = Log(logger)


class Client:
    """Клиент"""

    def __init__(self, name, addr='localhost', port=7777, mode='r'):
        """
        :param addr: адрес
        :param port: порт
        :param mode: чтение или запись
        """
        self.name = name
        self.addr = addr
        self.port = port
        self.mode = mode
        # Создаем клиенский репозиторий
        self.repo = DbRepo('{}.db'.format(self.name), Base)

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
        self.socket.send(bytes(presence_msg))

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
        self.socket.send(bytes(list_message))
        # Принять не более 1024 байтов данных
        message_bytes = self.socket.recv(1024)
        # Формируем сообщение из байт
        jm = JimResponse.create_from_bytes(message_bytes)
        if jm.response == ACCEPTED:
            # Ждем второе сообщение со списком контактов
            message_bytes = self.socket.recv(1024)
            jm = JimMessage.create_from_bytes(message_bytes)
            # выводим список контактов
            contact_list = jm.action
            print(contact_list)
            # обновляем наш список контактов, на сервере правильный
            self.repo.clear_contacts()
            for contact in contact_list:
                self.repo.add_contact(contact)
            return contact_list

    def add_contact(self, username):
        # формируем сообщение на добавления контакта
        add_message = JimMessage(action=ADD_CONTACT, user_id=username, time=time.time(), user=self.name)
        # отправляем сообщение на сервер
        self.socket.send(bytes(add_message))
        # получаем ответ от сервера
        # Принять не более 1024 байтов данных
        message_bytes = self.socket.recv(1024)
        # Формируем сообщение из байт
        jm = JimResponse.create_from_bytes(message_bytes)
        if jm.response == OK:
            print('Новый контакт {} успешно добавлен'.format(username))
            # Добавляем в свою базу контактов
            self.repo.add_contact(username)
            try:
                # FIXME: написать проверку на уникальность
                self.repo.commit()
            except:
                pass

    def del_contact(self, username):
        # формируем сообщение на добавления контакта
        message = JimMessage(action=DEL_CONTACT, user_id=username, time=time.time(), user=self.name)
        # отправляем сообщение на сервер
        self.socket.send(bytes(message))
        # получаем ответ от сервера
        # Принять не более 1024 байтов данных
        message_bytes = self.socket.recv(1024)
        # Формируем сообщение из байт
        jm = JimResponse.create_from_bytes(message_bytes)
        if jm.response == OK:
            print('Контакт {} успешно удален'.format(username))
            # удаляем контакт из своей базы
            self.repo.del_contact(username)
            self.repo.commit()

    def send_message(self, to, text):
        # формируем сообщение
        message = JimMessage(**{ACTION: MSG, TO: to, FROM: self.name, MESSAGE: text, TIME: time.time()})
        # отправляем
        self.socket.send(bytes(message))
        # получаем ответ
        message_bytes = self.socket.recv(1024)
        jm = JimResponse.create_from_bytes(message_bytes)
        if jm.response == ACCEPTED:
            print('Сообщение доставлено')
        else:
            print('Сообщение не доставлено')
            print(jm.response)

    def main_loop(self):
        print('Сервер дал добро работаем')
        if self.mode == 'r':
            # читаем сообщения и выводим на экран
            while True:
                # Принять не более 1024 байтов данных
                message_bytes = self.socket.recv(1024)
                # Формируем сообщение из байт
                jm = JimMessage.create_from_bytes(message_bytes)
                # Выводим только текст сообщения
                # print(jm.__dict__['from'])
                print(jm.__dict__['from'])
                print(jm.message)
        elif self.mode == 'w':
            # ждем ввода сообщения и шлем на сервер
            while True:
                # Тут будем добавлять контакты и получать список контактов
                message_str = input(':) >')
                if message_str.startswith('add'):
                    # добавляем контакт
                    # получаем имя пользователя
                    try:
                        username = message_str.split()[1]
                    except IndexError:
                        print('Не указано имя пользователя')
                    else:
                        self.add_contact(username)
                elif message_str.startswith('del'):
                    # удаляем контакт
                    # получаем имя пользователя
                    try:
                        username = message_str.split()[1]
                    except IndexError:
                        print('Не указано имя пользователя')
                    else:
                        self.del_contact(username)
                elif message_str == 'list':
                    self.get_contacts()
                elif message_str.startswith('message'):
                    params = message_str.split()
                    try:
                        to = params[1]
                        text = params[2]
                    except IndexError:
                        print('Не задан получатель или текст сообщения')
                    else:
                        self.send_message(to, text)
                elif message_str == 'help':
                    print('add <имя пользователя> - добавить контакт')
                    print('del <имя пользователя> - удалить контакт')
                    print('list - список контактов')
                else:
                    print('Неверная команда, для справки введите help')
        else:
            raise WrongModeError(mode)


if __name__ == '__main__':
    # Получаем параметры скрипта
    try:
        addr = sys.argv[1]
    except IndexError:
        addr = 'localhost'
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 7777
    except ValueError:
        print('Порт должен быть целым числом')
        sys.exit(0)
    try:
        mode = sys.argv[3]
        if mode not in ('r', 'w'):
            print('Режим должен быть r - чтение, w - запись')
            sys.exit(0)
    except IndexError:
        mode = 'w'
    try:
        name = sys.argv[4]
        print(name)
    except IndexError:
        name = 'Guest'

    client = Client(name, addr, port, mode)
    client.connect()
    client.main_loop()
    client.disconnect()