from jim.protocol import JimMessage, JimResponse
from jim.errors import MandatoryKeyError
from jim.config import MESSAGE
from PyQt5.QtCore import QObject, pyqtSignal


class Receiver:
    ''' Класс-получатель информации из сокета
    '''

    def __init__(self, sock, request_queue):
        # запоминаем очередь ответов
        self.request_queue = request_queue
        # запоминаем сокет
        self.sock = sock
        self.is_alive = False

    def process_message(self, message):
        pass

    def poll(self):
        self.is_alive = True
        while True:
            if not self.is_alive:
                break
            data = self.sock.recv(2**20)
            if data:
                try:
                    # Если нам пришло сообщение
                    jm = JimMessage.create_from_bytes(data)
                    # Если это message
                    if MESSAGE in jm:
                        # Печатаем в нормальном виде
                        self.process_message(jm)
                    else:
                        # Добавляем сообщение в очередь т.к. это серверное сообщение
                        self.request_queue.put(jm)
                except MandatoryKeyError:
                    # Если нам пришел ответ от сервера мы его добавляем в очередь для дальнейшей обработки
                    jr = JimResponse.create_from_bytes(data)
                    # При этом поток приостанавливается
                    self.request_queue.put(jr)
            else:
                break

    def stop(self):
        self.is_alive = False


class ConsoleReciever(Receiver):

    def process_message(self, message):
        print("\n>> user {}: {}".format(message.__dict__['from'], message.message))


class GuiReciever(Receiver, QObject):
    gotData = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, sock, request_queue):
        Receiver.__init__(self, sock, request_queue)
        QObject.__init__(self)

    def process_message(self, message):
        self.gotData.emit('{} >>> {}: {}'.format(message.__dict__['from'], message.__dict__['to'],  message.message))

    def poll(self):
        super().poll()
        self.finished.emit(0)
