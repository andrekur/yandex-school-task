from unittest import TestCase
from os import remove
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base
from api.api_start import app
from api.views import get_db

TEST_DB_PATH = './tests/test.db'

SQLALCHEMY_DATABASE_URL = F'sqlite:///{TEST_DB_PATH}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread''': False}
)
TestingSessionLocal = sessionmaker(autocommit=False,
                                   autoflush=False,
                                   bind=engine)


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


