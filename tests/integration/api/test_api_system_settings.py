from collections.abc import Sequence

from app.extensions import db
from app.models.users import User
from app.models.system_settings import SystemSetting, default_system_settings_base


def test_get_system_settings_result(
    logged_in_no_permissions_client, default_system_settings: Sequence[SystemSetting]
):
    with logged_in_no_permissions_client:
        response = logged_in_no_permissions_client.get('/api/system-settings')
        returned_system_settings = response.json
        assert len(returned_system_settings) == len(default_system_settings)
        for expected_setting in default_system_settings:
            returned_value = returned_system_settings[expected_setting.key]
            assert returned_value == expected_setting.value


def test_update_system_settings_persistence(
    logged_in_admin_client,
    default_system_settings: Sequence[SystemSetting]
):
    system_settings_update = {
        'default_temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
        'minimum_temperature_value': -20,
        'maximum_temperature_value': 30,
    }
    with logged_in_admin_client:
        response = logged_in_admin_client.put(
            '/api/system-settings',
            json=system_settings_update
        )
        assert response.status_code == 204
        updated_system_settings = db.session.execute(
            db.select(SystemSetting)
        ).scalars().all()
        for setting in updated_system_settings:
            assert setting.value == str(system_settings_update[setting.key])

def test_update_system_settings_rejects_non_admin_users(
    logged_in_no_permissions_client,
    default_system_settings: Sequence[SystemSetting]
):
    with logged_in_no_permissions_client:
        response = logged_in_no_permissions_client.put('/api/system-settings', json={
            'default_temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            'minimum_temperature_value': -20,
            'maximum_temperature_value': 30,
        })
        assert response.status_code == 403

def test_update_system_settings_invalid(
    logged_in_admin_client,
    default_system_settings: Sequence[SystemSetting]
):
    with logged_in_admin_client:
        response = logged_in_admin_client.put('/api/system-settings', json={
            'wrong': 123
        })
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_update_system_settings_invalid_temperature_unit(
    logged_in_admin_client,
    default_system_settings: Sequence[SystemSetting]
):
    with logged_in_admin_client:
        response = logged_in_admin_client.put('/api/system-settings', json={
            'default_temperature_unit': 'wrong',
            'minimum_temperature_value': -20,
            'maximum_temperature_value': 30,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_update_system_settings_invalid_too_low_minimum_temperature_value(
    logged_in_admin_client,
    default_system_settings: Sequence[SystemSetting]
):
    with logged_in_admin_client:
        response = logged_in_admin_client.put('/api/system-settings', json={
            'default_temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            'minimum_temperature_value':
                default_system_settings_base['minimum_temperature_value']['min'] - 1,
            'maximum_temperature_value': 30,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'value_limits'

def test_update_system_settings_invalid_too_high_minimum_temperature_value(
    logged_in_admin_client,
    default_system_settings: Sequence[SystemSetting]
):
    with logged_in_admin_client:
        response = logged_in_admin_client.put('/api/system-settings', json={
            'default_temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            'minimum_temperature_value':
                default_system_settings_base['minimum_temperature_value']['max'] + 1,
            'maximum_temperature_value': 30,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'value_limits'

def test_update_system_settings_invalid_too_low_maximum_temperature_value(
    logged_in_admin_client,
    default_system_settings: Sequence[SystemSetting]
):
    with logged_in_admin_client:
        response = logged_in_admin_client.put('/api/system-settings', json={
            'default_temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            'minimum_temperature_value': -20,
            'maximum_temperature_value':
                default_system_settings_base['maximum_temperature_value']['min'] - 1,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'value_limits'

def test_update_system_settings_invalid_too_high_maximum_temperature_value(
    logged_in_admin_client,
    default_system_settings: Sequence[SystemSetting]
):
    with logged_in_admin_client:
        response = logged_in_admin_client.put('/api/system-settings', json={
            'default_temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            'minimum_temperature_value': -20,
            'maximum_temperature_value':
                default_system_settings_base['maximum_temperature_value']['max'] + 1,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'value_limits'


# TODO: test /system-settings/last-update-time
