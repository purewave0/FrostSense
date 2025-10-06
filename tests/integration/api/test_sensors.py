from typing import Any

from tests.integration.api.util import _parsed_datetime
from app.models.readings import Sensor
from app.extensions import db


def test_sensors_order_and_result(
    sensors: tuple[Sensor, Sensor, Sensor],
    logged_in_admin_client
):
    response = logged_in_admin_client.get('/api/sensors')
    returned_sensors: list[dict[str, Any]] | None = response.json
    assert returned_sensors is not None
    assert len(returned_sensors) == len(sensors)

    for returned_sensor, expected_sensor in zip(
        returned_sensors, sensors
    ):
        assert returned_sensor['id'] == expected_sensor.id
        assert returned_sensor['name'] == expected_sensor.name
        assert (
            _parsed_datetime(returned_sensor['created_on'])
            == expected_sensor.created_on
        )


def test_update_sensor_persistence(app, sensor, logged_in_admin_client):
    response = logged_in_admin_client.put(
        f'/api/sensors/{sensor.id}',
        json={'name': 'Updated sensor'},
    )
    assert response.status_code == 204
    with app.app_context():
        updated_name = db.session.execute(
            db.select(
                Sensor.name
            ).where(
                Sensor.id == sensor.id
            )
        ).scalar_one()
        assert updated_name == 'Updated sensor'

def test_update_sensor_name_trimming(app, sensor, logged_in_admin_client):
    response = logged_in_admin_client.put(
        f'/api/sensors/{sensor.id}',
        json={'name': '     Updated sensor     '},
    )
    assert response.status_code == 204
    with app.app_context():
        updated_name = db.session.execute(
            db.select(
                Sensor.name
            ).where(
                Sensor.id == sensor.id
            )
        ).scalar_one()
        assert updated_name == 'Updated sensor'

def test_update_sensor_invalid_field(sensor, logged_in_admin_client):
    response = logged_in_admin_client.put(
        f'/api/sensors/{sensor.id}',
        json={'wrong': 123},
    )
    assert response.status_code == 400
    assert response.json['error'] == 'field_error'

def test_update_sensor_invalid_too_short_name(sensor, logged_in_admin_client):
    response = logged_in_admin_client.put(
        f'/api/sensors/{sensor.id}',
        json={'name': ''},
    )
    assert response.status_code == 400
    assert response.json['error'] == 'invalid_name_length'

def test_update_sensor_invalid_too_long_name(sensor, logged_in_admin_client):
    response = logged_in_admin_client.put(
        f'/api/sensors/{sensor.id}',
        json={'name': 'a' * (Sensor.MAX_NAME_LENGTH+1)},
    )
    assert response.status_code == 400
    assert response.json['error'] == 'invalid_name_length'

def test_update_sensor_invalid_duplicate_name(sensors, logged_in_admin_client):
    response = logged_in_admin_client.put(
        f'/api/sensors/{sensors[0].id}',
        json={'name': sensors[1].name},
    )
    assert response.status_code == 400
    assert response.json['error'] == 'name_already_exists'

def test_update_sensor_unknown_sensor(logged_in_admin_client):
    response = logged_in_admin_client.put(
        '/api/sensors/123',
        json={'name': 'Unknown sensor'},
    )
    assert response.status_code == 404
