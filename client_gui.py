import sys
from PyQt5 import QtWidgets, uic
import threading
from PyQt5.QtCore import Qt, QThread, pyqtSlot
from client import Client
from handlers import GuiReciever
from PyQt5.QtWidgets import QMessageBox

#я
name = input("What is your name?")
# Создаем приложение
app = QtWidgets.QApplication(sys.argv)
# грузим главную форму
window = uic.loadUi('main_win.ui')
window.setWindowTitle(name)
# создаем клиента на запись
client = Client(name=name)
# получаем список контактов с сервера, которые лежат у нас - не надежные
client.connect()

listener = GuiReciever(client.socket, client.request_queue)
# Связываем сигнал и слот
# слот обновление данных в списке сообщений


@pyqtSlot(str)
def update_chat(data):
    ''' Отображение сообщения в истории
    '''
    try:
        msg = data
        window.listWidgetMessages.addItem(msg)
    except Exception as e:
        print(e)


# сигнал мы берем из нашего GuiReciever
listener.gotData.connect(update_chat)


# Используем QThread так рекомендуется, но можно и обычный
#th_listen = threading.Thread(target=listener.poll)
#th_listen.daemon = True
#th_listen.start()
th = QThread()
listener.moveToThread(th)

# # ---------- Важная часть - связывание сигналов и слотов ----------
# При запуске потока будет вызван метод search_text
th.started.connect(listener.poll)
th.start()

contact_list = client.get_contacts()


def load_contacts(contacts):
    """загрузка контактов в список"""
    # чистим список
    window.listWidgetContacts.clear()
    # добавляем
    for contact in contacts:
        window.listWidgetContacts.addItem(contact)


# грузим контакты в список сразу при запуске приложения
load_contacts(contact_list)


def add_contact():
    """Добавление контакта"""
    # Получаем имя из QTextEdit
    username = window.textEditName.toPlainText()
    if username:
        # добавляем контакт - шлем запрос на сервер ...
        client.add_contact(username)
        # добавляем имя в QListWidget
        window.listWidgetContacts.addItem(username)


# Связываем сигнал нажатия кнопки добавить со слотом функцией добавить контакт
window.pushButtonAddContact.clicked.connect(add_contact)

# TODO в поле для ввода пользователя добавить подсказку ("...введите имя пользователя...")


def del_contact():
    """Удаление контакта"""
    # получаем выбранный элемент в QListWidget
    current_item = window.listWidgetContacts.currentItem()
    # получаем текст - это имя нашего контакта
    username = current_item.text()
    # удаление контакта (отправляем запрос на сервер)
    client.del_contact(username)
    # удаляем контакт из QListWidget
    # window.listWidgetContacts.removeItemWidget(current_item) - так не работает
    # del current_item
    # Так норм удаляется, может быть можно как то проще
    current_item = window.listWidgetContacts.takeItem(window.listWidgetContacts.row(current_item))
    del current_item


# связываем сигнал нажатия на кнопку и слот функцию удаления контакта
window.pushButtonDelContact.clicked.connect(del_contact)


def show_help():
    """Показывает всплывающее окно с подсказками"""
    QMessageBox.information(window, "What to do", "Add contact: add  <user name>,\nDelete contact: del  <user name>")


window.pushButtonHelp.clicked.connect(show_help)


def open_chat():
    try:
        """Открытие модального чата (модальное для демонстрации)"""
        # грузим QDialog чата
        dialog = uic.loadUi('chat_maia.ui')

        # получаем выделенного пользователя
        selected_index = window.listWidgetContacts.currentIndex()
        # получаем имя пользователя
        user_name = selected_index.data()
        # выставляем имя в название окна
        dialog.setWindowTitle(user_name)

        # отправка сообщения
        def send_message():
            text = dialog.textEdit.toPlainText()
            if text:
                client.send_message(user_name, text)
                # будем выводить то что мы отправили в общем чате
                msg = '{} >>> {}'.format(name, text)
                window.listWidgetMessages.addItem(msg)

        # связываем отправку с кнопкой ОК
        dialog.Send.clicked.connect(send_message)
        # запускаем в модальном режиме
        # привязываем события модального окна (для демонстрации)
        dialog.Send.clicked.connect(dialog.accept)
        dialog.Dont.clicked.connect(dialog.reject)
        dialog.exec()
    except Exception as e:
        print(e)
# Пока мы не можем передать элемент на который нажали - сделать в следующий раз через наследование


window.listWidgetContacts.itemDoubleClicked.connect(open_chat)


# Контекстное меню при нажатии правой кнопки мыши (пока тестовый вариант для демонстрации)
# Создаем на листе
window.listWidgetContacts.setContextMenuPolicy(Qt.CustomContextMenu)
window.listWidgetContacts.setContextMenuPolicy(Qt.ActionsContextMenu)
quitAction = QtWidgets.QAction("Quit", None)
quitAction.triggered.connect(app.quit)
window.listWidgetContacts.addAction(quitAction)

# рисуем окно
window.show()
# точка запуска приложения
sys.exit(app.exec_())