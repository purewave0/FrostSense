from app.extensions import db
from app.dbapi import (
    create_system_settings_timestamp_if_needed,
    _update_system_settings_timestamp,
    get_system_settings_update_timestamp,
    create_missing_system_settings,
    update_system_settings,
    get_system_settings
)
from app.models.system_settings import (
    SystemSettingsTimestamp, SystemSetting, default_system_settings_base
)


# create

def test_create_system_settings_timestamp_if_needed_persistence(app):
    with app.app_context():
        create_system_settings_timestamp_if_needed()

        stored_system_settings_timestamp = db.session.execute(
            db.select(
                SystemSettingsTimestamp
            ).where(
                SystemSettingsTimestamp.id == 1
            )
        ).scalar_one_or_none()
        assert stored_system_settings_timestamp is not None

def test_create_missing_system_settings_persistence(app):
    with app.app_context():
        create_missing_system_settings()

        stored_system_settings = db.session.execute(
            db.select(
                SystemSetting
            )
        ).scalars().all()

        assert len(stored_system_settings) == len(default_system_settings_base)
        for setting in stored_system_settings:
            assert setting.key in default_system_settings_base
            assert str(
                default_system_settings_base[setting.key]['value']
            ) == setting.value


# get

def test_get_system_settings_result(app, default_system_settings):
    with app.app_context():
        returned_settings = get_system_settings()
        assert len(returned_settings) == len(default_system_settings)
        for setting in default_system_settings:
            assert returned_settings[setting.key] == str(setting.value)

def test_get_system_settings_update_timestamp_result(app, system_settings_timestamp):
    with app.app_context():
        returned_timestamp = get_system_settings_update_timestamp()

        assert returned_timestamp == system_settings_timestamp.updated_on


# update

def test_update_system_settings_timestamp_difference(app, system_settings_timestamp):
    with app.app_context():
        old_timestamp = system_settings_timestamp.updated_on
        _update_system_settings_timestamp()
        db.session.commit()

        stored_system_settings_timestamp = db.session.execute(
            db.select(
                SystemSettingsTimestamp
            ).where(
                SystemSettingsTimestamp.id == 1
            )
        ).scalar_one()
        assert stored_system_settings_timestamp.updated_on > old_timestamp

def test_update_system_settings_persistence(app, default_system_settings):
    with app.app_context():
        update = {
            'default_temperature_unit': 'celsius',
            'minimum_gauge_value': -30,
            'maximum_gauge_value':  40,
            'minimum_graph_value': -30,
            'maximum_graph_value':  40,
        }
        update_system_settings(update)

        stored_system_settings = db.session.execute(
            db.select(SystemSetting)
        ).scalars().all()

        assert len(stored_system_settings) == len(default_system_settings)
        for setting in stored_system_settings:
            assert setting.key in default_system_settings_base
            assert setting.value == str(update[setting.key])
