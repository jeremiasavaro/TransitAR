import pytest
from app import app as _app
from infrastructure.database.session import get_db

from tests.fixtures.database import override_get_db

_app.dependency_overrides[get_db] = override_get_db

# Import fixtures so pytest discovers them
from tests.fixtures.auth import auth_headers, registered_user  # noqa: E402, F401
from tests.fixtures.client import client  # noqa: E402, F401


@pytest.fixture()
def app_instance():
    return _app
