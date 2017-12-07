class NoneClientError(Exception):

    def __init__(self, username):
        self.username = username

    def __str__(self):
        return 'Клиент с именем {} не найден'.format(self.username)


class NoneAvatarError(Exception):
    pass
