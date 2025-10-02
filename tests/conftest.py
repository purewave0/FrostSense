import pytest

from app import create_app
from config import TestingConfig
from app.extensions import db
from app.models.readings import Sensor


@pytest.fixture()
def app():
    app = create_app(TestingConfig)

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def sensor(app):
    """Create a sensor named 'Test sensor' and return it."""
    with app.app_context():
        created_sensor = Sensor('Test sensor')
        db.session.add(created_sensor)
        db.session.commit()
        yield created_sensor


@pytest.fixture()
def sensors(app):
    """Create three sensors named 'Test sensor 1', 'Test sensor 2', and
    'Test sensor 3', respectively, and return them.
    """
    with app.app_context():
        created_sensors = (
            Sensor('Test sensor 1'),
            Sensor('Test sensor 2'),
            Sensor('Test sensor 3'),
        )
        for sensor in created_sensors:
            db.session.add(sensor)
        db.session.commit()
        yield created_sensors
