import pytest
from app import app as _app
from infrastructure.database.base import Base
from infrastructure.database.session import get_db

from tests.fixtures.database import override_get_db, test_engine

_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _setup_schema():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

# Import fixtures so pytest discovers them
from tests.fixtures.auth import auth_headers, registered_user  # noqa: E402, F401
from tests.fixtures.client import client  # noqa: E402, F401


@pytest.fixture()
def app_instance():
    return _app
