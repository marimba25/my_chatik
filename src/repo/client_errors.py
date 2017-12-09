class NoneContactError(Exception):
    """Не найден контакт"""

    def __init__(self, username):
        self.username = username

    def __str__(self):
        return 'Контакт с именем {} не найден'.format(self.username)