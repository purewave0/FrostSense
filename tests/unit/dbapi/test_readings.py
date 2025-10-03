from collections.abc import Sequence
from datetime import datetime

from app.extensions import db
from app.dbapi import (
    create_reading,
    create_readings,
    get_sensor_readings_in_time_range,
    get_sensor_readings_count_in_time_range,
    get_sensors_readings_in_time_ranges,
    get_sensor_last_reading_by_id,
    get_sensors_last_readings_by_ids,
)
from app.models.readings import Sensor, Reading


# create

def test_create_reading_result_and_persistence(app, sensor):
    with app.app_context():
        reading = create_reading(sensor.id, 10.0)
        assert reading['id'] is not None
        assert reading['sensor_id'] == sensor.id
        assert reading['temperature'] == 10.0
        assert reading['created_on'] is not None

        stored_reading = db.session.execute(
            db.select(
                Reading
            ).where(
                Reading.id == reading['id']
            )
        ).scalar_one_or_none()
        assert stored_reading is not None
        assert stored_reading.sensor_id == sensor.id
        assert stored_reading.temperature == 10.0

def test_create_readings_persistence(app, sensor):
    readings = (
        {'temperature': -40.0, 'created_on': datetime(2025, 10, 1, 12, 34, 56)},
        {'temperature': 0.0,   'created_on': datetime(2025, 10, 1, 12, 35, 57)},
        {'temperature': 40.0,  'created_on': datetime(2025, 10, 2, 10, 11, 22)},
    )

    with app.app_context():
        create_readings(sensor.id, readings)

        stored_readings: Sequence[Reading] = db.session.execute(
            db.select(
                Reading
            ).where(
                Reading.sensor_id == sensor.id
            )
        ).scalars().all()

        assert len(stored_readings) == len(readings)
        for stored_reading, created_reading in zip(stored_readings, readings):
            assert stored_reading.temperature == created_reading['temperature']
            assert stored_reading.created_on == created_reading['created_on']


# get

def test_get_sensor_readings_in_time_range_order_and_result(app, sensor):
    readings = (
        Reading(sensor.id, -30, datetime(2025, 10, 1, 10, 36, 0)),
        Reading(sensor.id, -20, datetime(2025, 10, 1, 10, 37, 0)),
        Reading(sensor.id, -10, datetime(2025, 10, 1, 10, 38, 0)),
        Reading(sensor.id,   0, datetime(2025, 10, 1, 10, 39, 0)),
        Reading(sensor.id,  10, datetime(2025, 10, 1, 10, 40, 0)),
        Reading(sensor.id,  20, datetime(2025, 10, 1, 10, 41, 0)),
        Reading(sensor.id,  30, datetime(2025, 10, 1, 10, 42, 0)),
    )
    with app.app_context():
        for reading in readings:
            db.session.add(reading)
        db.session.commit()

        expected_readings = readings[3:6]

        # start after the second reading
        offset_id = readings[1].id

        returned_readings = get_sensor_readings_in_time_range(
            sensor.id,
            offset_id,
            datetime(2025, 10, 1, 10, 39, 0),
            datetime(2025, 10, 1, 10, 41, 0),
        )
        assert len(returned_readings) == len(expected_readings)
        for returned_reading, expected_reading in zip(
            returned_readings, expected_readings
        ):
            assert returned_reading['id'] == expected_reading.id
            assert returned_reading['temperature'] == expected_reading.temperature
            assert returned_reading['created_on'] == expected_reading.created_on

def test_get_sensor_readings_count_in_time_range_result(app, sensor):
    readings = (
        Reading(sensor.id, -30, datetime(2025, 10, 1, 10, 36, 0)),
        Reading(sensor.id, -20, datetime(2025, 10, 1, 10, 37, 0)),
        Reading(sensor.id, -10, datetime(2025, 10, 1, 10, 38, 0)),
        Reading(sensor.id,   0, datetime(2025, 10, 1, 10, 39, 0)),
        Reading(sensor.id,  10, datetime(2025, 10, 1, 10, 40, 0)),
        Reading(sensor.id,  20, datetime(2025, 10, 1, 10, 41, 0)),
        Reading(sensor.id,  30, datetime(2025, 10, 1, 10, 42, 0)),
    )
    with app.app_context():
        for reading in readings:
            db.session.add(reading)
        db.session.commit()

        expected_readings = readings[3:6]

        returned_count = get_sensor_readings_count_in_time_range(
            sensor.id,
            datetime(2025, 10, 1, 10, 39, 0),
            datetime(2025, 10, 1, 10, 41, 0),
        )
        assert returned_count == len(expected_readings)

def test_get_sensors_readings_in_time_range_result_items_order_and_result(app, sensors):
    sensors_readings: dict[int, tuple[Reading, ...]] = {}

    with app.app_context():
        for sensor in sensors:
            readings = (
                Reading(sensor.id, -30, datetime(2025, 10, 1, 10, 36, 0)),
                Reading(sensor.id, -20, datetime(2025, 10, 1, 10, 37, 0)),
                Reading(sensor.id, -10, datetime(2025, 10, 1, 10, 38, 0)),
                Reading(sensor.id,   0, datetime(2025, 10, 1, 10, 39, 0)),
                Reading(sensor.id,  10, datetime(2025, 10, 1, 10, 40, 0)),
                Reading(sensor.id,  20, datetime(2025, 10, 1, 10, 41, 0)),
                Reading(sensor.id,  30, datetime(2025, 10, 1, 10, 42, 0)),
            )
            sensors_readings[sensor.id] = readings
            for reading in readings:
                db.session.add(reading)
        db.session.commit()

        expected_sensors_readings: dict[int, tuple[Reading, ...]] = {}
        for sensor_id in sensors_readings:
            readings = sensors_readings[sensor_id]
            expected_sensors_readings[sensor_id] = readings[3:6]

        # start after the second reading for all of them
        offsets = []
        for sensor_id in sensors_readings:
            readings = sensors_readings[sensor_id]
            offsets.append(readings[2].id)

        returned_sensors_readings = get_sensors_readings_in_time_ranges(
            (sensor.id for sensor in sensors),
            offsets,
            (
                {
                    'start': datetime(2025, 10, 1, 10, 39, 0),
                    'end': datetime(2025, 10, 1, 10, 41, 0),
                } for _ in sensors
            )
        )
        assert len(returned_sensors_readings) == len(sensors)

        for sensor_id in returned_sensors_readings:
            returned_readings = returned_sensors_readings[sensor_id]
            expected_readings = expected_sensors_readings[sensor_id]

            assert len(returned_readings) == len(expected_readings)
            for returned_reading, expected_reading in zip(
                returned_readings, expected_readings
            ):
                assert returned_reading['id'] == expected_reading.id
                assert returned_reading['temperature'] == expected_reading.temperature
                assert returned_reading['created_on'] == expected_reading.created_on

def test_get_sensor_last_reading_by_id_found_and_empty_result_and_not_found(
    app, sensor
):
    with app.app_context():
        readings = (
            Reading(sensor.id, 10.0, datetime(2025, 10, 1, 1)),
            Reading(sensor.id, 11.0, datetime(2025, 10, 1, 2)),
            Reading(sensor.id, 12.0, datetime(2025, 10, 1, 3)),
            # inserted *last* but, chronologically, the first
            Reading(sensor.id, 13.0, datetime(1, 1, 1))
        )
        for reading in readings:
            db.session.add(reading)
        db.session.commit()

        expected_last_reading = readings[-2]

        returned_last_reading = get_sensor_last_reading_by_id(sensor.id)
        assert returned_last_reading is not None
        assert returned_last_reading['id'] == expected_last_reading.id
        assert returned_last_reading['temperature'] == expected_last_reading.temperature
        assert returned_last_reading['created_on'] == expected_last_reading.created_on

        empty_sensor = Sensor('Empty sensor')
        db.session.add(empty_sensor)
        db.session.commit()

        assert get_sensor_last_reading_by_id(empty_sensor.id) is None

        assert get_sensor_last_reading_by_id(12345) is None

def test_get_sensors_last_readings_by_ids_found_and_empty_result_and_not_found(
    app, sensors
):
    sensors_readings: dict[int, tuple[Reading, ...]] = {}

    with app.app_context():
        for sensor in sensors:
            readings = (
                Reading(sensor.id, 10.0, datetime(2025, 10, 1, 1)),
                Reading(sensor.id, 11.0, datetime(2025, 10, 1, 2)),
                Reading(sensor.id, 12.0, datetime(2025, 10, 1, 3)),
                # inserted *last* but, chronologically, the first
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

        returned_sensors_last_readings = get_sensors_last_readings_by_ids(
            (sensor.id for sensor in sensors)
        )
        assert len(returned_sensors_last_readings) == len(expected_sensors_last_readings)
        for sensor_id in returned_sensors_last_readings:
            returned_last_reading = returned_sensors_last_readings[sensor_id]
            expected_last_reading = expected_sensors_last_readings[sensor_id]

            assert returned_last_reading is not None
            assert returned_last_reading['id'] == expected_last_reading.id
            assert returned_last_reading['temperature'] == expected_last_reading.temperature
            assert returned_last_reading['created_on'] == expected_last_reading.created_on

        empty_sensors = (
            Sensor('Empty sensor 1'),
            Sensor('Empty sensor 2'),
            Sensor('Empty sensor 3'),
        )
        for sensor in empty_sensors:
            db.session.add(sensor)
        db.session.commit()

        returned_empty_sensors_last_readings = get_sensors_last_readings_by_ids(
            (sensor.id for sensor in empty_sensors)
        )
        for sensor_id in returned_empty_sensors_last_readings:
            assert returned_empty_sensors_last_readings[sensor_id] is None

        unknown_sensor_ids = (1234, 2345, 3456)
        returned_unknown_sensors_last_readings = get_sensors_last_readings_by_ids(
            unknown_sensor_ids
        )
        for sensor_id in unknown_sensor_ids:
            assert returned_unknown_sensors_last_readings[sensor_id] is None


# TODO: test get_sensors_readings_counts_since_today_by_ids
