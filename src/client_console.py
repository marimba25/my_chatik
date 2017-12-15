import sys
from client import Client
from handlers import ConsoleReciever
import threading

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

name = input("What is your name?") or 'Guest'



client = Client(name, addr, port)
client.connect()

listener = ConsoleReciever(client.socket, client.request_queue)
th_listen = threading.Thread(target=listener.poll)
th_listen.daemon = True
th_listen.start()
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
            client.add_contact(username)
    elif message_str.startswith('del'):
        # удаляем контакт
        # получаем имя пользователя
        try:
            username = message_str.split()[1]
        except IndexError:
            print('Не указано имя пользователя')
        else:
            client.del_contact(username)
    elif message_str == 'list':
        contacts = client.get_contacts()
    elif message_str.startswith('message'):
        params = message_str.split()
        try:
            to = params[1]
            text = params[2]
        except  IndexError:
            print('Не задан отправитель или текст сообщения')
        else:
            client.send_message(to, text)
    elif message_str == 'help':
        print('add <имя пользователя> - добавить контакт')
        print('del <имя пользователя> - удалить контакт')
        print('list - список контактов')
        print('exit - выход')
    elif message_str == 'exit':
        break
    else:
        print('Неверная команда, для справки введите help')