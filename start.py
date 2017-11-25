# Служебный скрипт запуска/останова нескольких клиентских приложений

from subprocess import Popen
import time
import random

# список запущенных процессов
p_list = []
TWO = True
SERVER_PATH = 'server.py'
CLIENT_PATH = 'client_console.py'
CLIENT_GUI_PATH = 'client_gui.py'

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
        # запускаем консольных клиентов
        CONSOLE_COUNT = 2
        for i in range(CONSOLE_COUNT):
            # Запускаем клиентский скрипт и добавляем его в список процессов
            print('Запуск консольного клиента')
            client_name = 'Console{}'.format(i)
            print(client_name)
            p_list.append(Popen(['xterm', '-hold', '-e', 'python3 {} localhost 7777 {}'.format(CLIENT_PATH, client_name)],
                                 shell=False))

        # запускаем гуи клиентов
        GUI_COUNT = 1
        for i in range(GUI_COUNT):
            # запускаем клиентский скрипт и добавляем его в список процессов
            print("Запуск гуи клиента")
            client_name = 'Gui{}'.format(i)
            print(client_name)
            p_list.append(
                Popen(['xterm', '-hold', '-e', 'python3 {}'.format(CLIENT_GUI_PATH)],
                      shell=False))
        print('Клиенты звпущены')

    elif user == 'q':
        print('Открыто процессов {}'.format(len(p_list)))
        for p in p_list:
            print('Закрываю {}'.format(p))
            p.kill()
        p_list.clear()
        print('Выхожу')
        break
