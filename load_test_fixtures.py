from datetime import datetime

from dbModels.Subscriber import Subscriber
from dbModels.User import User
from services.DatabaseService import DatabaseService

db = DatabaseService().get_db()


def prepare_db():
    db.create_tables([User, Subscriber])


def load_subscriber():
    return Subscriber.create(name="DefaultSubscriber", description="Master subscriber account not actual subscriber",
                             subscriber_key="Ds4GlQNozwQHaHBVFHXhlrZABuLHE2CXOl81HUyf2RqMH08j8mbcYofJfQWDT3If",
                             can_authenticate=True, can_register=True, active=True, created=datetime.now())


print(prepare_db())
print(load_subscriber())