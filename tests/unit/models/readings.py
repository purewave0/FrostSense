import re

from app.extensions import db
from app.models.readings import Sensor, Reading


sensor_key_pattern = re.compile(r'[a-zA-Z0-9]{24}')

# sensors

def test_sensor_model(app):
    with app.app_context():
        sensor = Sensor('Test sensor')
        db.session.add(sensor)
        db.session.commit()

        stored_sensor: Sensor | None = db.session.execute(
            db.select(
                Sensor
            ).where(
                Sensor.id == sensor.id
            )
        ).scalar_one_or_none()
        assert stored_sensor is not None
        assert sensor_key_pattern.match(stored_sensor.key)
        assert stored_sensor == sensor

def test_sensor_generate_key_format(app, sensor: Sensor):
    assert sensor_key_pattern.match(Sensor.generate_key())


# readings

def test_reading_model(app, sensor: Sensor):
    with app.app_context():
        reading = Reading(sensor.id, 12.34)
        db.session.add(reading)
        db.session.commit()

        stored_reading: Reading | None = db.session.execute(
            db.select(
                Reading
            ).where(
                Reading.id == reading.id
            )
        ).scalar_one_or_none()
        assert stored_reading is not None
        assert stored_reading.sensor_id == sensor.id
        assert stored_reading.temperature == 12.34
        assert stored_reading == reading
