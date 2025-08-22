from collections.abc import Iterable
from datetime import datetime
from typing import Any

from flask import current_app

from app.extensions import db
from app.models.readings import Sensor, Reading
from app.models.users import User


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


def get_sensor_ids() -> tuple[int]:
    """Return all sensor IDs."""
    result = db.session.execute(
        db.select(Sensor.id)
    )

    return tuple(result.scalars())


def get_sensor_name(sensor_id: int) -> str:
    """Return the name of the sensor with the given ID."""
    result = db.session.execute(
        db.select(
            Sensor.name
        ).where(
            Sensor.id == sensor_id
        )
    ).scalar_one()

    return result


def sensor_id_exists(sensor_id: int) -> bool:
    """Return whether a sensor with the given ID exists."""
    # TODO: case-insensitiveness
    result = db.session.execute(
        db.select(
            db.exists().where(Sensor.id == sensor_id)
        )
    ).scalar_one()

    return result


def sensor_name_exists(name: str) -> bool:
    """Return whether a sensor with the given name exists."""
    # TODO: case-insensitiveness
    result = db.session.execute(
        db.select(
            db.exists().where(Sensor.name == name)
        )
    ).scalar_one()

    return result


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
    sensor_id: int,
    offset_id: int | None,
    range_start: datetime,
    range_end: datetime
) -> tuple[dict[str, Any], ...]:
    """Return the readings in the given time range from the given sensor.

    Args:
        sensor_id: The ID of the Sensor to fetch the readings from.
        offset_id: The reading ID to start fetching after.
        range_start: The start (inclusive) of the time range.
        range_end: The end (inclusive) of the time range.
    """
    query =  db.select(
        Reading.id,
        Reading.temperature,
        Reading.created_on,
    ).where(
        Reading.created_on >= range_start,
        Reading.created_on <= range_end,
        Reading.sensor_id == sensor_id
    ).order_by(
        Reading.created_on.asc()
    )

    if offset_id:
        query = query.where(Reading.id > offset_id)

    result = db.session.execute(query)

    return _rows_to_dicts(result)

def get_sensors_readings_in_time_ranges(
    sensors_ids: Iterable[int],
    offset_ids: Iterable[int] | None,
    time_ranges: Iterable[dict[str, datetime]]
) -> dict[int, tuple[dict[str, Any], ...]]:
    """Return the readings in the given time ranges for each given sensor.

    Args:
        sensor_ids: The IDs of the Sensors to fetch the readings from.
        offset_ids: The reading IDs to start fetching after, one for each sensor.
        time_ranges: A collection of time ranges, one for each sensor. A time range
            is a dict in the form of {'start': <datetime>, 'end': <datetime>}, both
            points inclusive.
    """

    if offset_ids:
        return {
            sensor_id: get_sensor_readings_in_time_range(
                sensor_id, offset_id, time_range['start'], time_range['end']
            )
            for sensor_id, offset_id, time_range
                in zip(sensors_ids, offset_ids, time_ranges)
        }

    return {
        sensor_id: get_sensor_readings_in_time_range(
            sensor_id, None, time_range['start'], time_range['end']
        )
        for sensor_id, time_range in zip(sensors_ids, time_ranges)
    }


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


def get_sensor_last_reading(
    sensor_id: int
) -> dict[str, Any] | None:
    """Get the last reading from the given sensor. Useful for gauges.

    Args:
        sensor_id: The ID of the Sensor to fetch the last reading from.
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
        ).limit(1)
    ).one_or_none()

    if not result:
        return None

    return result._asdict()


def get_sensors_last_readings(
    sensor_ids: Iterable[int]
) -> dict[int, dict[str, Any] | None]:
    """Get the last reading from each given sensor. Useful for gauges.

    Args:
        sensor_ids: The IDs of the Sensors to fetch the last readings from.
    """
    return {
        sensor_id: get_sensor_last_reading(sensor_id)
        for sensor_id in sensor_ids
    }


def get_sensor_latest_readings(
    sensor_id: int, limit: int
) -> tuple[dict[str, Any], ...]:
    """Get the last N readings from the given sensor. Useful for populating a graph.

    Args:
        sensor_id: The ID of the Sensor to fetch the readings from.
        offset: The reading ID to start fetching after.
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

    # reversing so that oldest comes first, newest comes last
    return _rows_to_dicts(result)[::-1]


def get_sensors_latest_readings(
    sensor_ids: Iterable[int], limit: int
) -> dict[int, tuple]:
    """Get the last N readings from each given sensor. Useful for populating graphs.

    Args:
        sensor_ids: The IDs of the Sensors to fetch the readings from.
        limit: The max number of readings to fetch from each sensor.
    """
    return {
        sensor_id: get_sensor_latest_readings(sensor_id, limit)
        for sensor_id in sensor_ids
    }


def get_sensors_readings_counts_since_today(sensor_ids: Iterable[int]) -> dict[int, int]:
    """Get the amount of readings sent today for each sensor.

    "Today" means since midnight (00:00:00) in the server's time.

    Args:
        sensor_ids: The IDs of the Sensors to fetch the readings count from.
    """
    # TODO: get 'midnight' not in the server's time, but the user's?
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


# -- auth --

def get_user_by_username(username: str) -> User | None:
    """Return the User with the given username, or None."""
    user = db.session.execute(
        db.select(
            User
        ).where(
            User.username == username
        )
    ).scalar_one_or_none()

    return user


def create_user(display_name: str, username: str, password: str) -> User:
    """Create a user in the database.

    Args:
        display_name: The name others will see. Must be between User.MIN_NAME_LENGTH and
            User.MAX_NAME_LENGTH characters.
        username: The name used for logging in. Must be between User.MIN_NAME_LENGTH and
            User.MAX_NAME_LENGTH characters.
        password: The password. Must be between User.MIN_PASSWORD_LENGTH and
            User.MAX_PASSWORD_LENGTH characters.

    Returns:
        The newly created User object.
    """
    user = User(display_name, username, password)

    db.session.add(user)
    db.session.commit()

    return user


def update_user(
    user_id: int,
    display_name: str,
    username: str,
    homepage: User.WebPage,
    temperature_unit: User.TemperatureUnit
) -> None:
    """Update a user in the database.

    Args:
        display_name: The name that others will see.
        username: The name used for logging in.
        homepage: The first page the user sees after logging in.
        temperature_unit: The unit used to display temperatures.
    """
    db.session.execute(
        db.update(
            User
        ).where(
            User.id == user_id
        )
        .values(
            display_name=display_name,
            username=username,
            homepage=homepage,
            temperature_unit=temperature_unit,
        )
    )
    db.session.commit()
