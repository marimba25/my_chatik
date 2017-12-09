"""Все ошибки клиента и сервера"""


class WrongModeError(Exception):
    """Неверный режим запуска"""

    def __init__(self, mode):
        self.mode = mode

    def __str__(self):
        return 'Неверный режим запуска {}. Режим запуска должен быть r - чтение или w - запись'.format(self.mode)