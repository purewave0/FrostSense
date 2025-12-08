from datetime import datetime

from app.models.readings import Reading
from app.extensions import db
from tests.util import parsed_datetime


def test_get_sensors_last_readings_result(app, sensors, logged_in_admin_client):
    sensors_readings: dict[int, tuple[Reading, ...]] = {}

    with app.app_context():
        for sensor in sensors:
            readings = (
                Reading(sensor.id, 10.0, datetime(2025, 10, 1, 1)),
                Reading(sensor.id, 11.0, datetime(2025, 10, 1, 2)),
                Reading(sensor.id, 12.0, datetime(2025, 10, 1, 3)),
                Reading(sensor.id, 13.0, datetime(1, 1, 1))
            )
            sensors_readings[sensor.id] = readings
            for reading in readings:
                db.session.add(reading)
        db.session.commit()

        expected_sensors_last_readings: dict[int, Reading] = {}
        for sensor_id in sensors_readings:
            readings = sensors_readings[sensor_id]
            expected_sensors_last_readings[sensor_id] = readings[-2]

        response = logged_in_admin_client.get('/api/sensors/last-readings')
        returned_sensors_last_readings = response.json
        assert returned_sensors_last_readings is not None
        assert len(returned_sensors_last_readings) == len(expected_sensors_last_readings)

        for sensor_id in returned_sensors_last_readings:
            returned_last_reading = returned_sensors_last_readings[sensor_id]
            expected_last_reading = expected_sensors_last_readings[int(sensor_id)]

            assert returned_last_reading is not None
            assert returned_last_reading['id'] == expected_last_reading.id
            assert returned_last_reading['temperature'] == expected_last_reading.temperature
            assert parsed_datetime(
                returned_last_reading['created_on']
            ) == expected_last_reading.created_on

def test_get_sensors_last_readings_empty(sensors, logged_in_admin_client):
    response = logged_in_admin_client.get('/api/sensors/last-readings')
    returned_sensors_last_readings = response.json
    assert returned_sensors_last_readings is not None
    for sensor_id in returned_sensors_last_readings:
        assert returned_sensors_last_readings[sensor_id] is None


# TODO: test_get_sensors_readings_by_day(app, sensors):


def test_send_sensor_reading(app, sensor, client):
    response = client.post(
        f'/api/sensors/{sensor.id}/readings',
        json={'temperature': -12.34},
        headers={'Authorization': sensor.key}
    )
    assert response.status_code == 201
    with app.app_context():
        stored_readings = db.session.execute(
            db.select(
                Reading
            ).where(
                Reading.sensor_id == sensor.id
            )
        ).scalars().all()
        assert len(stored_readings) == 1
        assert stored_readings[0].temperature == -12.34

def test_send_sensor_reading_unauthorised(sensor, logged_in_admin_client):
    response = logged_in_admin_client.post(
        f'/api/sensors/{sensor.id}/readings',
        json={'temperature': -12.34},
        headers={'Authorization': 'wrong'}
    )
    assert response.status_code == 401

def test_send_sensor_reading_invalid(sensor, logged_in_admin_client):
    response = logged_in_admin_client.post(
        f'/api/sensors/{sensor.id}/readings',
        json={'wrong': 123},
        headers={'Authorization': 'wrong'}
    )
    assert response.status_code == 400

def test_send_sensor_reading_unknown_sensor(sensor, logged_in_admin_client):
    response = logged_in_admin_client.post(
        '/api/sensors/1234/readings',
        json={'temperature': -12.34},
        headers={'Authorization': sensor.key}
    )
    assert response.status_code == 404


# TODO: test_api_sensor_readings_count


# TODO: test_api_sensors_today_readings_count
