import pytest
from db import db
from app import create_app


@pytest.fixture(scope="session")
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as testclient:
        with app.app_context():
            db.create_all()
            yield testclient

    with app.app_context():
        db.session.remove()
        db.drop_all()
