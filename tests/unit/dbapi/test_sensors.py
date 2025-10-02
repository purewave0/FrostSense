from app.extensions import db
from app.dbapi import (
    create_sensor,
    delete_sensor_by_id,
    get_sensors, get_sensor_by_id,
    get_sensor_ids, get_sensor_key_by_id,
    sensor_id_exists, sensor_name_exists,
    reset_sensor_key_by_id, update_sensor_by_id,
)
from app.models.readings import Sensor


# create

def test_create_sensor_result_and_persistence(app):
    with app.app_context():
        sensor = create_sensor('Test sensor')
        assert sensor['id'] is not None
        assert sensor['name'] == 'Test sensor'
        assert sensor['created_on'] is not None

        stored_sensor = db.session.execute(
            db.select(
                Sensor
            ).where(
                Sensor.id == sensor['id']
            )
        ).scalar_one_or_none()
        assert stored_sensor is not None
        assert stored_sensor.name == 'Test sensor'


# delete

def test_delete_sensor_by_id_persistence(app):
    sensor = Sensor('Test sensor')
    with app.app_context():
        db.session.add(sensor)
        db.session.commit()

        delete_sensor_by_id(sensor.id)

        stored_sensor = db.session.execute(
            db.select(
                Sensor
            ).where(
                Sensor.id == sensor.id
            )
        ).scalar_one_or_none()
        assert stored_sensor is None


# retrieve

def test_get_sensors_order_and_result(app):
    with app.app_context():
        added_sensors = [
            Sensor('Test sensor 1'),
            Sensor('Test sensor 2'),
            Sensor('Test sensor 3'),
        ]
        for sensor in added_sensors:
            db.session.add(sensor)
        db.session.commit()

        returned_sensors = get_sensors()
        assert len(returned_sensors) == len(added_sensors)

        for returned_sensor, added_sensor in zip(
            returned_sensors, added_sensors
        ):
            assert returned_sensor['id'] == added_sensor.id
            assert returned_sensor['name'] == added_sensor.name
            assert returned_sensor['created_on'] == added_sensor.created_on

def test_get_sensor_by_id_found_and_not_found(app):
    sensor = Sensor('Test sensor')
    with app.app_context():
        db.session.add(sensor)
        db.session.commit()

        found = get_sensor_by_id(sensor.id)
        assert found is not None
        assert found.id == sensor.id
        assert found.name == 'Test sensor'

        assert get_sensor_by_id(12345) is None


# retrieve attribute

def test_get_sensor_ids_order_and_result(app):
    added_sensors: list[Sensor] = []
    names = ['Test sensor 1', 'Test sensor 2', 'Test sensor 3']
    with app.app_context():
        for name in names:
            sensor = Sensor(name)
            db.session.add(sensor)
            added_sensors.append(sensor)
        db.session.commit()

        returned_sensor_ids = get_sensor_ids()
        assert len(returned_sensor_ids) == len(added_sensors)

        for returned_sensor_id, added_sensor in zip(
            returned_sensor_ids, added_sensors
        ):
            assert returned_sensor_id == added_sensor.id

def test_get_sensor_key_by_id_found_and_not_found(app):
    sensor = Sensor('Test sensor')
    with app.app_context():
        db.session.add(sensor)
        db.session.commit()

        found = get_sensor_key_by_id(sensor.id)
        assert found == sensor.key

        assert get_sensor_key_by_id(12345) is None


# exists

def test_sensor_id_exists_found_and_not_found(app):
    sensor = Sensor('Test sensor')
    with app.app_context():
        db.session.add(sensor)
        db.session.commit()

        assert sensor_id_exists(sensor.id)

        assert not sensor_id_exists(12345)

def test_sensor_name_exists_found_and_not_found(app):
    sensor = Sensor('Test sensor')
    with app.app_context():
        db.session.add(sensor)
        db.session.commit()

        assert sensor_name_exists('Test sensor')

        assert not sensor_name_exists('Unknown sensor')


# update

def test_reset_sensor_key_by_id_result_and_difference(app):
    sensor = Sensor('Test sensor')
    with app.app_context():
        db.session.add(sensor)
        db.session.commit()
        old_key = sensor.key

        new_key = reset_sensor_key_by_id(sensor.id)
        assert new_key == sensor.key

        assert old_key != sensor.key

def test_update_sensor_by_id_persistence(app):
    sensor = Sensor('Test sensor')
    with app.app_context():
        db.session.add(sensor)
        db.session.commit()

        update_sensor_by_id(sensor.id, 'Updated test sensor')

        assert sensor.name == 'Updated test sensor'
