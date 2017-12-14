# Служебный скрипт запуска/останова нескольких клиентских приложений

from subprocess import Popen, TimeoutExpired
import time
import random
from client import Client
import platform

# список запущенных процессов
p_list = []
TWO = True
SERVER_PATH = 'server.py'
CLIENT_PATH = 'client_console.py'
CLIENT_GUI_PATH = 'client_gui.py'

system = platform.system()

if system not in ['Linux', 'Windows']:
    print('Неподдерживаемая операционная система')
    exit(1)

if system == 'Windows':
    from subprocess import CREATE_NEW_CONSOLE

while True:
    user = input("Запустить сервер и клиентов (s) / Выйти (q)")

    if user == 's':
        # запускаем сервер
        # Запускаем серверный скрипт и добавляем его в список процессов
        if system == 'Linux':
            p_list.append(Popen(['xterm', '-hold', '-e', 'python3 {}'.format(SERVER_PATH)],
                                shell=False))
        elif system == 'Windows':
            p_list.append(Popen('python {}'.format(SERVER_PATH),
                                creationflags=CREATE_NEW_CONSOLE))
        print('Сервер запущен')
        # ждем на всякий пожарный
        time.sleep(1)
        # запускаем консольных клиентов
        CONSOLE_COUNT = 0
        for i in range(CONSOLE_COUNT):
            # Запускаем клиентский скрипт и добавляем его в список процессов
            print('Запуск консольного клиента')
            if system == 'Linux':
                p_list.append(Popen(['xterm', '-hold', '-e', 'python3 {} localhost 7777'.format(CLIENT_PATH)],
                                    shell=False))
            elif system == 'Windows':
                p_list.append(Popen('python {} localhost 7777'.format(CLIENT_PATH),
                                    creationflags=CREATE_NEW_CONSOLE))

        # запускаем гуи клиентов
        GUI_COUNT = 3
        for i in range(GUI_COUNT):
            # запускаем клиентский скрипт и добавляем его в список процессов
            print("Запуск гуи клиента")

            client_name = 'Guest{}'.format(i)
            if system == 'Linux':
                p_list.append(
                    Popen(['python3', CLIENT_GUI_PATH],
                          shell=False))
            elif system == 'Windows':
                Popen('python {}'.format(CLIENT_GUI_PATH),
                      creationflags=CREATE_NEW_CONSOLE)
        print('Клиенты запущены')

    elif user == 'q':
        print('Открыто процессов {}'.format(len(p_list)))
        for p in p_list:
            try:
                print('Закрываю {}'.format(p))
                p.wait(0.5)
            except TimeoutExpired:
                print('Убиваю {}'.format(p))
                p.kill()
        p_list.clear()
        print('Выхожу')
        break
