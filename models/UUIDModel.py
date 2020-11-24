from peewee import *
from services.DatabaseService import DatabaseService

db = DatabaseService().get_db()


class UUIDModel(Model):
    id = UUIDField(primary_key=True)

    class Meta:
        database = db
