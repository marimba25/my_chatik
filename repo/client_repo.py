from .client_models import Contact, Message
from .client_errors import NoneContactError
from .repo import DbBaseRepo


class DbRepo(DbBaseRepo):
    """Клиентский репозиторий"""

    def add_contact(self, username):
        """Добавление контакта по имени"""
        new_item = Contact(username)
        self.session.add(new_item)

    def del_contact(self, username):
        """Удаление контакта по имени"""
        contact = self._get_contact_by_username(username)
        self.session.delete(contact)

    def _get_contact_by_username(self, username):
        """Получение контакта по имени"""
        contact = self.session.query(Contact).filter(Contact.Name == username).first()
        return contact

    def get_contacts(self):
        """Получение всех контактов"""
        contacts = self.session.query(Contact)
        return contacts

    def add_message(self, username, text):
        """
        Добавление сообщения
        :param username: имя пользователя
        :param text: текст сообщения
        :return: None
        """
        contact = self._get_contact_by_username(username)
        if contact:
            new_item = Message(text=text, contact_id=contact.ContactId)
            self.session.add(new_item)
        else:
            raise NoneContactError(username)

    def clear_contacts(self):
        # Удаление всех контактов
        self.session.query(Contact).delete()