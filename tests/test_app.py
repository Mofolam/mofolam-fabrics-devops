import os

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///:memory:"
)

import pytest

from app.app import app
from app.models import db


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Mofolam Fabrics" in response.data
