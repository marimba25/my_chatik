from .server_models import Client, ClientHistory, ClientContact, Avatar
from .server_errors import NoneClientError, NoneAvatarError
from .repo import DbBaseRepo


class DbRepo(DbBaseRepo):
    """Серверное хранилище"""

    def add_client(self, username, info=None):
        """Добавление клиента"""
        new_item = Client(username, info)
        print(new_item)
        self.session.add(new_item)

    def client_exists(self, username):
        """Проверка, что клиент уже есть"""
        result = self.session.query(Client).filter(Client.Name == username).count() > 0
        return result

    def _get_client_by_username(self, username):
        """Получение клиента по имени"""
        client = self.session.query(Client).filter(Client.Name == username).first()
        return client

    def add_history(self, username, ip):
        """Добавление истории"""
        client = self._get_client_by_username(username)
        if client:
            history = ClientHistory(client_id=client.ClientId, ip=ip)
            self.session.add(history)
        else:
            raise NoneClientError(username)

    def add_contact(self, client_username, contact_username):
        """Добавление контакта"""
        contact = self._get_client_by_username(contact_username)
        if contact:
            client = self._get_client_by_username(client_username)
            if client:
                cc = ClientContact(client_id=client.ClientId, contact_id=contact.ClientId)
                print(cc)
                self.session.add(cc)
            else:
                raise NoneClientError(client_username)
        else:
            raise NoneClientError(contact_username)

    def add_avatar(self, client_username, avatar_data):
        """Добавление аватара"""
        client = self._get_client_by_username(client_username)
        if client:
            avatar = Avatar(client.ClientId, avatar_data)
            self.session.add(avatar)
        else:
            raise NoneClientError(client_username)

    def get_avatar(self, client_username):
        """Добавление аватара"""
        client = self._get_client_by_username(client_username)
        if client:
            avatar_record = self.session.query(Avatar).filter(Avatar.ClientId == client.ClientId).order_by(
                Avatar.ID.desc()).first()
            if avatar_record:
                return avatar_record.Avatar
            else:
                raise NoneAvatarError()
        else:
            raise NoneClientError(client_username)

    def del_contact(self, client_username, contact_username):
        """Удаление контакта"""
        contact = self._get_client_by_username(contact_username)
        if contact:
            client = self._get_client_by_username(client_username)
            if client:
                cc = self.session.query(ClientContact).filter(
                    ClientContact.ClientId == client.ClientId).filter(
                    ClientContact.ContactId == contact.ClientId).first()
                self.session.delete(cc)
            else:
                raise NoneClientError(contact_username)
        else:
            raise NoneClientError(client_username)

    def get_contacts(self, client_username):
        """Получение контактов клиента"""
        client = self._get_client_by_username(client_username)
        if client:
            # Тут нету relationship поэтому берем запросом
            contacts_clients = self.session.query(ClientContact).filter(ClientContact.ClientId == client.ClientId)
            result = []
            for contact_client in contacts_clients:
                contact = self.session.query(Client).filter(Client.ClientId == contact_client.ContactId).first()
                result.append(contact.Name)
            return result
        else:
            raise NoneClientError(client_username)

    def get_clients(self):
        """Получение всех клиентов"""
        return self.session.query(Client).all()

    def get_histories(self):
        """Получение всех историй"""
        return self.session.query(ClientHistory).all()
