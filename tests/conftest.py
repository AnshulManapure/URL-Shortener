from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app.models import Base
from app.main import app
from app.main import get_db

from dotenv import load_dotenv
import os

load_dotenv()

#Create a testing db
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD")
TEST_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@localhost:5432/URL_Shortener_Test"

engine = create_engine(TEST_DATABASE_URL)
TestingSession = sessionmaker(bind=engine)

#Create a fixture that runs before each test to drop all tables and recreate them
@pytest.fixture(scope="function", autouse=True)
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSession()

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield session

    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def clear_redis():
    from app.cache import redis_client
    redis_client.flushall()