# Служебный скрипт запуска/останова нескольких клиентских приложений

from subprocess import Popen
import time
import random

# список запущенных процессов
p_list = []
TWO = True
SERVER_PATH = 'server.py'
CLIENT_PATH = 'client.py'

while True:
    user = input("Запустить сервер и клиентов (s) / Выйти (q)")

    if user == 's':
        # запускаем сервер
        # Запускаем серверный скрипт и добавляем его в список процессов
        p_list.append(Popen(['xterm', '-hold', '-e',  'python3 {}'.format(SERVER_PATH)],
                            shell=False))
        print('Сервер запущен')
        # ждем на всякий пожарный
        time.sleep(1)
        # запускаем клиентов на чтение
        READ_COUNT = 1 if TWO else random.randint(1, 10)
        for i in range(READ_COUNT):
            # Запускаем клиентский скрипт и добавляем его в список процессов
            print('Запуск клиента')
            client_name = 'Reader{}'.format(i)
            print(client_name)
            p_list.append(Popen(['xterm', '-hold', '-e', 'python3 {} localhost 7777 r {}'.format(CLIENT_PATH, client_name)],
                                 shell=False))
        print('Клиенты на чтение запущены')
        # запускаем клиента на запись
        WRITE_COUNT = 1 if TWO else random.randint(1, 5)
        for i in range(WRITE_COUNT):
            # Запускаем клиентский скрипт и добавляем его в список процессов
            client_name = 'Writer{}'.format(i)
            print(client_name)
            p_list.append(Popen(['xterm', '-hold', '-e', 'python3 {} localhost 7777 w {}'.format(CLIENT_PATH,
                                                                            client_name)], shell=False))
        print('Клиенты на запись запущены')
    elif user == 'q':
        print('Открыто процессов {}'.format(len(p_list)))
        for p in p_list:
            print('Закрываю {}'.format(p))
            p.kill()
        p_list.clear()
        print('Выхожу')
        break