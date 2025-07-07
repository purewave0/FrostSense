from collections.abc import Iterable

from flask import current_app
from sqlalchemy.engine.result import ScalarResult

from app.extensions import db
from app.models.readings import Sensor, Reading


# TODO: TypedDicts for models?

def _rows_to_dicts(rows):
    """Convert the given Rows from a SQLAlchemy query into a tuple of dicts."""
    return tuple(row._asdict() for row in rows)


# -- sensors --

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


def get_sensors() -> tuple[dict]:
    """Return all sensors."""
    result = db.session.execute(
        db.select(
            Sensor.id,
            Sensor.name
        )
    )

    return _rows_to_dicts(result)


def get_sensor_ids() -> ScalarResult:
    """Return all sensor IDs."""
    result = db.session.execute(
        db.select(Sensor.id)
    )

    return result.scalars()


# -- readings --

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

def create_readings(sensor_id: int, readings: Iterable[dict]) -> None:
    """Insert multiple readings from the given sensor.

    Args:
        sensor_id: The ID of the Sensor the readings belong to.
        readings: The readings. Each reading is a dict with the following keys:
            {id: int, temperature: float, created_on: datetime}
    """
    # TODO: created_on parameter
    for reading in readings:
        db.session.add(
            Reading(
                sensor_id, reading['temperature'], reading['created_on']
            )
        )

    current_app.logger.info(f'mass-creating readings for sensor_id={sensor_id}')

    db.session.commit()


def get_latest_readings_from_sensor(sensor_id: int, limit: int) -> tuple[dict]:
    """Get the last N readings from the given sensor. Useful for populating a graph.

    Args:
        sensor_id: The ID of the Sensor to fetch the readings from.
        limit: The max number of readings to fetch from the sensor.
    """
    result = db.session.execute(
        db.select(
            Reading.id,
            Reading.temperature,
            Reading.created_on,
        ).where(
            Reading.sensor_id == sensor_id
        ).order_by(
            Reading.created_on.desc()
        ).limit(
            limit
        )
    )

    return _rows_to_dicts(result)


def get_latest_readings_from_sensors(
    sensor_ids: Iterable[int], limit: int
) -> dict[int, tuple]:
    """Get the last N readings from the given sensors. Useful for populating graphs.

    Args:
        sensor_ids: The IDs of the Sensors to fetch the readings from.
        limit: The max number of readings to fetch from each sensor.
    """
    return {
        sensor_id: get_latest_readings_from_sensor(sensor_id, limit)
        for sensor_id in sensor_ids
    }
