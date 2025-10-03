from datetime import datetime

import pytest

from app import create_app
from config import TestingConfig
from app.extensions import db
from app.models.readings import Sensor
from app.models.users import User
from app.models.system_settings import (
    SystemSetting, SystemSettingsTimestamp, default_system_settings_base
)


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


@pytest.fixture()
def user(app):
    """Create and return a user named 'Test user 1', username 'testuser1', non-temporary
    password 'password1', no permissions (beyond viewing sensors & readings), Readings
    as the homepage and Celsius as the preferred temperature unit.
    """
    with app.app_context():
        created_user = User(
            'Test user 1',
            'testuser1',
            'password1',
            False,
            User.Permission(0),
            User.WebPage.READINGS,
            User.TemperatureUnit.CELSIUS,
        )
        db.session.add(created_user)
        db.session.commit()
        yield created_user


@pytest.fixture()
def users(app):
    """Create and return three users named 'Test user 1' (username 'testsensor1',
    non-temporary password 'password1'), and so on.
    """
    with app.app_context():
        created_users = []
        for number in range(1, 3+1):
            created_user = User(
                f'Test user {number}',
                f'testuser{number}',
                f'password{number}',
                False,
                User.Permission(0),
                User.WebPage.READINGS,
                User.TemperatureUnit.CELSIUS,
            )
            db.session.add(created_user)
            created_users.append(created_user)
        db.session.commit()

        yield created_users


@pytest.fixture()
def admin(app):
    """Create and return a user named 'Administrator', username 'admin', non-temporary
    password 'password1', admin permissions, Readings as the homepage and Celsius as
    the preferred temperature unit.
    """
    with app.app_context():
        created_admin = User(
            'Administrator',
            'admin',
            'password1',
            False,
            User.Permission.ADMIN,
            User.WebPage.READINGS,
            User.TemperatureUnit.CELSIUS,
        )
        db.session.add(created_admin)
        db.session.commit()
        yield created_admin


@pytest.fixture()
def system_settings_timestamp(app):
    """Create and return a system setting timestamp with 'updated_on' set to now."""
    with app.app_context():
        created_timestamp = SystemSettingsTimestamp(updated_on=datetime.utcnow())
        db.session.add(created_timestamp)
        db.session.commit()
        yield created_timestamp


@pytest.fixture()
def default_system_settings(app):
    """Create and return the default system settings."""
    with app.app_context():
        created_system_settings = []
        for key in default_system_settings_base:
            setting = SystemSetting(
                key=key,
                value=default_system_settings_base[key]['value']
            )
            created_system_settings.append(setting)
            db.session.add(setting)
        db.session.commit()
        yield created_system_settings
