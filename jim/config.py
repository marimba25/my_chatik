"""Константы для работы JIM протокола"""
# Возможные ключи в сообщениях от клиентов
PRESENCE = 'presence'
MSG = 'msg'
QUIT = 'quit'
ADD_AVATAR = 'add_avatar'
GET_AVATAR = 'get_avatar'

# Кортеж возможных действий (будет дополняться)
ACTIONS = (PRESENCE, MSG, QUIT, ADD_AVATAR, GET_AVATAR)

# Обязательные ключи в сообщениях от клиента
ACTION = 'action'
TIME = 'time'

# Кортеж из обязательных ключей для сообщений от клиента
MANDATORY_MESSAGE_KEYS = (ACTION, TIME)

# Обязательные ключи в ответах сервера
RESPONSE = 'response'

# Кортеж обязательных ключей в ответах от сервера
MANDATORY_RESPONSE_KEYS = (RESPONSE,)

# Коды ответов (будут дополняться)
BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400  # неправильный запрос/json объект
SERVER_ERROR = 500

# Кортеж из кодов ответов
RESPONSE_CODES = (BASIC_NOTICE, OK, ACCEPTED, WRONG_REQUEST, SERVER_ERROR)

# Другие константы
USER = 'user'
ACCOUNT_NAME = 'account_name'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'
GET_CONTACTS = 'get_contacts'
QUANTITY = 'quantity'
TO = 'to'
FROM = 'from'
MESSAGE = 'message'