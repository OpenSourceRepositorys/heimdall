from peewee import *
from dbModels.BaseModel import BaseModel


class Subscriber(BaseModel):
    name = CharField()
    description = CharField()
    subscriber_key = CharField()
    can_authenticate = BooleanField()
    can_register = BooleanField()
    active = BooleanField()
    created = DateField()

