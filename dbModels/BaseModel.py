from peewee import *
from services.DatabaseService import DatabaseService

db = DatabaseService().get_db()


class BaseModel(Model):
    class Meta:
        database = db
