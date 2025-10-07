from datetime import datetime

from app.extensions import db
from app.models.system_settings import SystemSetting, SystemSettingsTimestamp


# system settings

def test_system_setting_model(app):
    with app.app_context():
        system_setting = SystemSetting(key='test_setting', value='test_value')
        db.session.add(system_setting)
        db.session.commit()

        stored_system_setting: SystemSetting | None = db.session.execute(
            db.select(
                SystemSetting
            ).where(
                SystemSetting.id == system_setting.id
            )
        ).scalar_one_or_none()
        assert stored_system_setting is not None
        assert stored_system_setting.key == 'test_setting'
        assert stored_system_setting.value == 'test_value'
        assert stored_system_setting == system_setting


# system settings timestamp

def test_timestamp_model(app):
    with app.app_context():
        timestamp_value = datetime.now()
        timestamp = SystemSettingsTimestamp(updated_on=timestamp_value)
        db.session.add(timestamp)
        db.session.commit()

        stored_timestamp: SystemSettingsTimestamp | None = db.session.execute(
            db.select(
                SystemSettingsTimestamp
            ).where(
                SystemSettingsTimestamp.id == timestamp.id
            )
        ).scalar_one_or_none()
        assert stored_timestamp is not None
        assert stored_timestamp.updated_on == timestamp_value
        assert stored_timestamp == timestamp
