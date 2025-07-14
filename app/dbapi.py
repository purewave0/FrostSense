from collections.abc import Iterable
from datetime import datetime
from typing import Any

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


def get_sensors() -> tuple[dict[str, Any], ...]:
    """Return all sensors."""
    result = db.session.execute(
        db.select(
            Sensor.id,
            Sensor.name,
            Sensor.created_on,
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
    reading = Reading(sensor_id, temperature)
    db.session.add(reading)
    db.session.commit()

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
    for reading in readings:
        db.session.add(
            Reading(
                sensor_id, reading['temperature'], reading['created_on']
            )
        )

    current_app.logger.info(f'mass-creating readings for sensor_id={sensor_id}')

    db.session.commit()


def get_sensor_readings_in_time_range(
    sensor_id: int, range_start: datetime, range_end: datetime
) -> tuple[dict[str, Any], ...]:
    """Return the readings in the given time range from the given sensor.

    Args:
        sensor_id: The ID of the Sensor to fetch the readings from.
        range_start: The start (inclusive) of the time range.
        range_end: The end (inclusive) of the time range.
    """
    result = db.session.execute(
        db.select(
            Reading.id,
            Reading.temperature,
            Reading.created_on,
        ).where(
            Reading.created_on >= range_start,
            Reading.created_on <= range_end,
            Reading.sensor_id == sensor_id
        ).order_by(
            Reading.created_on.desc()
        )
    )

    return _rows_to_dicts(result)


def get_sensor_readings_count_in_time_range(
    sensor_id: int, range_start: datetime, range_end: datetime
) -> int:
    """Return the amount of readings in the given time range from the given sensor.

    Args:
        sensor_id: The ID of the Sensor to count the readings from.
        range_start: The start (inclusive) of the time range.
        range_end: The end (inclusive) of the time range.
    """
    result = db.session.execute(
        db.select(
            db.func.count()
        ).select_from(
            Reading
        ).where(
            Reading.created_on >= range_start,
            Reading.created_on <= range_end,
            Reading.sensor_id == sensor_id
        ).order_by(
            Reading.created_on.desc()
        )
    ).scalar_one()

    return result


def get_latest_readings_from_sensor(
    sensor_id: int, limit: int
) -> tuple[dict[str, Any], ...]:
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


def get_today_readings_count_from_sensors(sensor_ids: Iterable[int]) -> dict[int, int]:
    """Get the amount of readings sent today for each sensor.

    "Today" means since midnight (00:00:00) in the server's time.

    Args:
        sensor_ids: The IDs of the Sensors to fetch the readings count from.
    """
    midnight_today = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    result = {}
    for sensor_id in sensor_ids:
        count = db.session.execute(
            db.select(
                db.func.count()
            ).select_from(
                Reading
            ).where(
                Reading.created_on > midnight_today,
                Reading.sensor_id == sensor_id
            )
        ).scalar()

        result[sensor_id] = count

    return result
