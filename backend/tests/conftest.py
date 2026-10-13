import pytest
from backend.app.database.session import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    init_db()
