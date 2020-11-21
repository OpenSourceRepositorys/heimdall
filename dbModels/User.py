from peewee import *
from dbModels.Subscriber import Subscriber
from dbModels.UUIDModel import UUIDModel


class User(UUIDModel):
    username = CharField()
    password = CharField()
    email = CharField()
    registered_by = ForeignKeyField(Subscriber, backref='users')
    active = BooleanField()
    created = DateField()
