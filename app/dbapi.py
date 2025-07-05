from flask import current_app

from app.extensions import db
from app.models.readings import Sensor, Reading


# TODO: TypedDicts for models?

def create_sensor(name: str) -> dict:
    sensor = Sensor(name)
    db.session.add(sensor)
    db.session.commit()


    current_app.logger.info(
        f'creating sensor name="{name}"',
    )

    return {
        'id': sensor.id,
        'name': sensor.name,
        'created_on': sensor.created_on,
    }
# TODO: edit sensor, delete sensor


def create_reading(sensor_id: int, temperature: float) -> dict:
    # TODO: created_on parameter
    reading = Reading(sensor_id, temperature)
    db.session.add(reading)
    db.session.commit()
    # TODO: catch error when the sensor doesn't exist

    current_app.logger.info(
        f'creating reading sensor_id={sensor_id} temperature={temperature}°C',
    )

    return {
        'id': reading.id,
        'sensor_id': reading.sensor_id,
        'temperature': reading.temperature,
        'created_on': reading.created_on,
    }
# TODO: mass creation of readings (when recovering from disruptions)
