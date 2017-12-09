import base64
import json
from .config import *
from .errors import MandatoryKeyError, ResponseCodeError, ResponseCodeLenError


class BaseJimMessage:
    """Базовое сообщение для JIM протокола"""

    def __init__(self, **kwargs):
        """
        :param kwargs: любые именованные параметры для формирования сообщения
        """
        for k, v in kwargs.items():
            # Формируем свойства нашего объекта динамически
            setattr(self, k, v)

    def __bytes__(self):
        """Возможность приводить сообщение сразу в байты bytes(jim_message)"""
        # Преобразуем в json
        message_json = json.dumps(self.__dict__)
        # Преобразуем в байты
        message_bytes = message_json.encode(encoding='utf-8')
        # Возвращаем рузльтат
        return message_bytes

    @classmethod
    def create_from_bytes(cls, message_bytes):
        """Возможность создавать сообщение по набору байт"""
        # Байты в json
        message_json = message_bytes.decode(encoding='utf-8')
        # json в словарь
        message_dict = json.loads(message_json)
        # создаем экземпляр нужного класса
        return cls(**message_dict)

    @staticmethod
    def bytes_to_base64str(bytes_input):
        return base64.encodebytes(bytes_input).decode('utf-8')

    @staticmethod
    def base64str_to_bytes(str_input):
        return base64.decodebytes(str_input.encode('utf-8'))

    def __str__(self):
        return str(self.__dict__)

    def __contains__(self, item):
        return item in self.__dict__


class JimMessage(BaseJimMessage):
    def __init__(self, **kwargs):
        """Реализуем проверки для сообщения с клиента"""
        if ACTION not in kwargs:
            raise MandatoryKeyError(ACTION)
        if TIME not in kwargs:
            raise MandatoryKeyError(TIME)
        super().__init__(**kwargs)


class JimResponse(BaseJimMessage):
    def __init__(self, **kwargs):
        """Реализуем проверки для отевта сервера"""
        if RESPONSE not in kwargs:
            raise MandatoryKeyError(RESPONSE)
        code = kwargs[RESPONSE]
        # длина кода не менее 3х символов
        if len(str(code)) != 3:
            raise ResponseCodeLenError(code)
        # неправильные коды символов
        if code not in RESPONSE_CODES:
            raise ResponseCodeError(code)
        super().__init__(**kwargs)
