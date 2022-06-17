from unittest import TestCase
from os import remove
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from db.models import Base
from api.api_start import app
from api.controllers import get_db

TEST_DB_PATH = './tests/test.db'

SQLALCHEMY_DATABASE_URL = F'sqlite:///{TEST_DB_PATH}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread''': False}
)
TestingSessionLocal = sessionmaker(autocommit=False,
                                   autoflush=False,
                                   bind=engine)


# without this foreign key not work in sqlite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class BaseAPITest(TestCase):
    client = TestClient(app)

    @classmethod
    def setUp(cls):
        Base.metadata.create_all(bind=engine)
        # create test BD
        app.dependency_overrides[get_db] = override_get_db

    @classmethod
    def tearDown(cls):
        # remove test db
        remove(TEST_DB_PATH)

    def post_imports(self, imports):
        # hardcoding url is wrong ¯\_(ツ)_/¯
        return self.client.post(
            '/imports',
            json={**imports}
        )

    def get_items(self, items_id):
        return self.client.get(
            f'/nodes/{items_id}'
        )

    def del_items(self, items_id):
        return self.client.delete(
            f'/delete/{items_id}'
        )


