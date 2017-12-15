import sys
from PyQt5 import QtWidgets, uic
import threading
from PyQt5.QtCore import Qt, QThread, pyqtSlot, QBuffer, QIODevice
from client import Client
from handlers import GuiReciever
from PyQt5.QtWidgets import QMessageBox, QAction, QTextEdit, QFileDialog, QInputDialog, QPushButton, QLineEdit, QWidget
from PyQt5.QtGui import QIcon, QFont, QTextCharFormat, QImage, QPixmap

# Создаем приложение
app = QtWidgets.QApplication(sys.argv)


def get_name():
    text, ok = QInputDialog.getText(None, 'Input name', 'What is your name')
    if ok:
        return text
    else:
        return 'Guest'


name = get_name()

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
    """Отображение сообщения в истории
    """
    try:
        msg = data
        window.textEditMessage.insertHtml(msg + "<br>")
    except Exception as e:
        print(e)

@pyqtSlot(int)
def listener_finished(data):
    client.disconnect()

# сигнал мы берем из нашего GuiReciever
listener.gotData.connect(update_chat)

listener.finished.connect(listener_finished)

# Используем QThread так рекомендуется, но можно и обычный
# th_listen = threading.Thread(target=listener.poll)
# th_listen.daemon = True
# th_listen.start()
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


def draw_avatar(image):
    pixmap = QPixmap.fromImage(image).scaled(140, 140, Qt.KeepAspectRatio)
    window.avatar.setPixmap(pixmap)


def set_avatar():
    """установка аватарки"""
    image_path = QFileDialog.getOpenFileName(window, 'Choose file', '', 'Images (*.jpg)')[0]
    image = QImage(image_path).scaled(256, 256, Qt.KeepAspectRatio)
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    image.save(buffer, 'JPG')
    client.add_my_avatar(buffer.data())
    draw_avatar(image)


window.pushButtonChangeAvatar.clicked.connect(set_avatar)


def load_avatar_from_local_db():
    return client.get_my_avatar()


def load_avatar_from_server():
    return client.get_my_avatar_from_server()


def load_avatar():
    avatar = load_avatar_from_server()
    if avatar:
        return avatar
    return load_avatar_from_local_db()


def draw_avatar_from_data(avatar):
    if not avatar:
        return
    image = QImage()
    image.loadFromData(avatar)
    draw_avatar(image)


def open_chat():
    try:
        """Открытие чата"""
        # грузим QDialog чата
        chatik = uic.loadUi('chatik_window.ui')

        # получаем выделенного пользователя
        selected_index = window.listWidgetContacts.currentIndex()
        # получаем имя пользователя
        user_name = selected_index.data()
        # выставляем имя в название окна
        chatik.setWindowTitle(user_name)

        def action_bold():
            my_font = QTextCharFormat()
            my_font.setFontWeight(QFont.Bold)
            chatik.textEdit.mergeCurrentCharFormat(my_font)

        def action_italic():
            my_font = QTextCharFormat()
            my_font.setFontItalic(True)
            chatik.textEdit.mergeCurrentCharFormat(my_font)

        def action_underlined():
            my_font = QTextCharFormat()
            my_font.setFontUnderline(True)
            chatik.textEdit.mergeCurrentCharFormat(my_font)

        bold = QAction(QIcon('icons/b.jpg'), 'Bold', chatik)
        italic = QAction(QIcon('icons/i.jpg'), 'Italic', chatik)
        underlined = QAction(QIcon('icons/u.jpg'), 'Underlined', chatik)

        toolbar = chatik.addToolBar('Formatting')
        toolbar.addAction(bold)
        toolbar.addAction(italic)
        toolbar.addAction(underlined)

        bold.triggered.connect(action_bold)
        italic.triggered.connect(action_italic)
        underlined.triggered.connect(action_underlined)

        def action_smile():
            url = 'icons/smile.png'
            chatik.textEdit.insertHtml('<img src="%s" />' % url)

        def action_sad():
            url = 'icons/sad.png'
            chatik.textEdit.insertHtml('<img src="%s" />' % url)

        def action_scared():
            url = 'icons/scared.png'
            chatik.textEdit.insertHtml('<img src="%s" />' % url)

        smile = QAction(QIcon('icons/smile.png'), 'Smile', chatik)
        sad = QAction(QIcon('icons/sad.png'), 'Sad', chatik)
        scared = QAction(QIcon('icons/scared'), 'Scared', chatik)

        toolbar = chatik.addToolBar('Smiles')
        toolbar.addAction(smile)
        toolbar.addAction(sad)
        toolbar.addAction(scared)

        smile.triggered.connect(action_smile)
        sad.triggered.connect(action_sad)
        scared.triggered.connect(action_scared)

        # отправка сообщения
        def send_message():
            text = chatik.textEdit.toHtml()
            if text:
                client.send_message(user_name, text)
                # будем выводить то что мы отправили в общем чате
                msg = '{} >>> {}: {}'.format(name, user_name, text)
                window.textEditMessage.insertHtml(msg + '<br>')

        # связываем отправку с кнопкой ОК
        chatik.Send.clicked.connect(send_message)
        # запускаем в модальном режиме
        # привязываем события модального окна (для демонстрации)
        chatik.Send.clicked.connect(chatik.close)
        chatik.Dont.clicked.connect(chatik.close)
        chatik.show()
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
draw_avatar_from_data(load_avatar())

# рисуем окно
window.show()
# точка запуска приложения
sys.exit(app.exec_())
