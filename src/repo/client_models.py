import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Binary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Contact(Base):
    """Наш клиент-пользователь мессенджера"""
    # назанвание таблицы
    __tablename__ = 'Contact'
    # первичный ключ
    ContactId = Column(Integer, primary_key=True)
    # имя-логин
    Name = Column(String, unique=True)

    def __init__(self, name):
        self.Name = name

    def __repr__(self):
        return "<Contact ('%s')>" % self.Name

    def __eq__(self, other):
        """2 контакта равные если равны их имена"""
        return self.Name == other.Name


class MyAvatar(Base):
    """Avatar"""
    # table name
    __tablename__ = 'MyAvatar'
    # primary key
    ID = Column(Integer, primary_key=True)
    Avatar = Column(Binary)

    def __init__(self, avatar_data):
        self.Avatar = avatar_data


class Message(Base):
    """Сообщение"""
    # имя таблицы
    __tablename__ = 'Message'
    # первичный ключ
    MessageId = Column(Integer, primary_key=True)
    # текст сообщения
    Text = Column(String)
    # дата содания по умолчанию сейчас
    CreatedDatetime = Column(DateTime, default=datetime.datetime.utcnow)
    # кто написал сообщение
    ContactId = Column(Integer, ForeignKey('Contact.ContactId'))
    # по сообщению можно получить контакт через обратную связку Message.Contact
    Contact = relationship("Contact", back_populates="Messages")

    def __init__(self, text, contact_id, creation_datetime=None):
        self.Text = text
        self.ContactId = contact_id
        # Если даты нету, то будет текущая
        if creation_datetime:
            self.CreatedDatetime = creation_datetime

    def __repr__(self):
        return "<Message ('%s', %d)>" % (self.Text, self.ContactId)

    def __eq__(self, other):
        # сообщение одинаковый, когда все поля кроме ключа одинаковые
        return self.Text == other.Text and self.CreatedDatetime == other.CreatedDatetime and self.ContactId == other.ContactId


# Обратная связь для удобного получения сообщений который написал пользователь Contat.Messages
Contact.Messages = relationship("Message", order_by=Message.CreatedDatetime, back_populates="Contact")