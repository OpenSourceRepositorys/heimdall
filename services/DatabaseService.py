from peewee import PostgresqlDatabase


class DatabaseService:
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    driver_configured = False

    def get_db(self):
        if not self.driver_configured:
            self.db_name = 'heimdall'
            self.db_user = 'postgres'
            self.db_password = 'ag.password'
            self.db_host = 'db'
            self.db_port = '5432'
            self.driver_configured = True

        return PostgresqlDatabase(self.db_name, user=self.db_user, password=self.db_password,
                                  host=self.db_host, port=self.db_port)
