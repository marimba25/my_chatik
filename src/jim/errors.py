class MandatoryKeyError(Exception):
    """Ошибка отсутствия обязательного ключа в сообщении"""

    def __init__(self, key):
        """
        :param key: обязательный ключ, которого нет в сообщении
        """
        self.key = key

    def __str__(self):
        return 'Не хватает обязательного атрибута {}'.format(self.key)


class ResponseCodeError(Exception):
    """Ошибка неверный код ответа от сервера"""

    def __init__(self, code):
        """
        :param code: Неверный код ответа
        """
        self.code = code

    def __str__(self):
        return 'Неверный код ответа {}'.format(self.code)


class ResponseCodeLenError(ResponseCodeError):
    """Ошибка неверная длина кода ответа, должна быть 3 символа"""

    def __str__(self):
        return 'Неверная длина кода {}. Длина кода должна быть 3 символа.'.format(self.code)