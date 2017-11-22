from pytest import raises
import time
from .protocol import JimMessage, JimResponse, BaseJimMessage
from .errors import MandatoryKeyError, ResponseCodeError, ResponseCodeLenError


class TestBaseJimMessage:
    def test_str(self):
        assert str(BaseJimMessage(action='msg')) == "{'action': 'msg'}"

    def test_create_from_bytes(self):
        # сообщение в байтах
        message = b'{"action": "msg"}'
        bjm = BaseJimMessage.create_from_bytes(message)
        assert isinstance(bjm, BaseJimMessage)
        assert str(bjm) == "{'action': 'msg'}"


class TestJimMessage:
    def test_init(self):
        # Не хватает атрибутов action или time
        with raises(MandatoryKeyError):
            JimMessage(time=time.time())
        with raises(MandatoryKeyError):
            JimMessage(action='msg')


class TestJimResponse:
    def test_init(self):
        # неверная длина кода ответа
        with raises(ResponseCodeLenError):
            JimResponse(response=5)
        # нету ключа response
        with raises(MandatoryKeyError):
            JimResponse(one='two')
        # неверный код ответа
        with raises(ResponseCodeError):
            JimResponse(response=700)

    def test_create_from_bytes(self):
        # сообщение в байтах
        message = b'{"response": 500}'
        # Нам интересен только что это тип JimResponse
        bjm = JimResponse.create_from_bytes(message)
        assert isinstance(bjm, JimResponse)
        assert str(bjm) == "{'response': 500}"