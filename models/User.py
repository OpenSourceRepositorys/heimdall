from peewee import *
from models.Subscriber import Subscriber
from models.UUIDModel import UUIDModel


class User(UUIDModel):
    username = CharField()
    password = CharField()
    email = CharField()
    registered_by = ForeignKeyField(Subscriber, backref='users')
    active = BooleanField()
    created = DateField()
