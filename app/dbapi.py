from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Any

from flask import current_app

from app.extensions import db
from app.models.readings import Sensor, Reading
from app.models.users import User
from app.models.system_settings import (
    SystemSetting, SystemSettingsTimestamp, default_system_settings_base
)


def _rows_to_dicts(rows):
    """Convert the given Rows from a SQLAlchemy query into a tuple of dicts."""
    return tuple(row._asdict() for row in rows)


# -- sensors --

def create_sensor(name: str) -> dict[str, Any]:
    """Create a sensor with the given name."""
    sensor = Sensor(name)
    db.session.add(sensor)
    db.session.commit()

    current_app.logger.debug(
        f'creating sensor name="{name}"',
    )

    return {
        'id': sensor.id,
        'name': sensor.name,
        'created_on': sensor.created_on,
    }


def delete_sensor_by_id(sensor_id: int) -> None:
    """Delete the sensor with the given id."""
    db.session.execute(
        db.delete(
            Sensor
        ).where(
            Sensor.id == sensor_id
        )
    )
    db.session.commit()


def get_sensors() -> tuple[dict[str, Any], ...]:
    """Return all sensors in order of creation."""
    result = db.session.execute(
        db.select(
            Sensor.id,
            Sensor.name,
            Sensor.created_on,
        ).order_by(
            Sensor.created_on.asc()
        )
    )

    return _rows_to_dicts(result)


def get_sensor_ids() -> tuple[int]:
    """Return all sensor IDs in order of creation."""
    result = db.session.execute(
        db.select(
            Sensor.id
        ).order_by(
            Sensor.created_on.asc()
        )
    )

    return tuple(result.scalars())


def sensor_id_exists(sensor_id: int) -> bool:
    """Return whether a sensor with the given ID exists."""
    result = db.session.execute(
        db.select(
            db.exists().where(Sensor.id == sensor_id)
        )
    ).scalar_one()

    return result


def sensor_name_exists(name: str) -> bool:
    """Return whether a sensor with the given name exists."""
    result = db.session.execute(
        db.select(
            db.exists().where(Sensor.name == name)
        )
    ).scalar_one()

    return result


def get_sensor_by_id(sensor_id: int) -> Sensor | None:
    """Return the sensor with the given ID."""
    result = db.session.execute(
        db.select(
            Sensor
        ).where(
            Sensor.id == sensor_id
        )
    ).scalar_one_or_none()

    return result


def get_sensor_key_by_id(sensor_id: int) -> str | None:
    """Return the key of the sensor with the given ID."""
    result = db.session.execute(
        db.select(
            Sensor.key
        ).where(
            Sensor.id == sensor_id
        )
    ).scalar_one_or_none()

    return result


def reset_sensor_key_by_id(sensor_id: int) -> str:
    """Reset the key of the sensor with the given ID and return the new key."""
    new_key = Sensor.generate_key()
    db.session.execute(
        db.update(
            Sensor
        ).where(
            Sensor.id == sensor_id
        ).values(
            key=new_key
        )
    )
    db.session.commit()

    return new_key


def update_sensor_by_id(
    sensor_id: int,
    name: str,
) -> None:
    """Update a sensor in the database."""

    db.session.execute(
        db.update(
            Sensor
        ).where(
            Sensor.id == sensor_id
        ).values(
            name=name,
        )
    )
    db.session.commit()


# -- readings --

def create_reading(sensor_id: int, temperature: float) -> dict:
    """Insert a reading from the given sensor.

    Args:
        sensor_id: The ID of the Sensor the reading belongs to.
        temperature: The temperature, in Celsius.
    """
    reading = Reading(sensor_id, temperature)
    db.session.add(reading)
    db.session.commit()

    current_app.logger.debug(
        f'creating reading sensor_id={sensor_id} temperature={temperature}°C',
    )

    return {
        'id': reading.id,
        'sensor_id': reading.sensor_id,
        'temperature': reading.temperature,
        'created_on': reading.created_on,
    }


def create_readings(sensor_id: int, readings: Iterable[dict]) -> None:
    """Retroactively insert multiple readings from the given sensor.

    Args:
        sensor_id: The ID of the Sensor the readings belong to.
        readings: The readings. Each reading is a dict with the following keys:
            {temperature: float, created_on: datetime}
    """
    for reading in readings:
        db.session.add(
            Reading(
                sensor_id, reading['temperature'], reading['created_on']
            )
        )

    current_app.logger.debug(f'mass-creating readings for sensor_id={sensor_id}')

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
    query = db.select(
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


def get_sensor_last_reading_by_id(
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


def get_sensors_last_readings_by_ids(
    sensor_ids: Iterable[int]
) -> dict[int, dict[str, Any] | None]:
    """Get the last reading from each given sensor. Useful for gauges.

    Args:
        sensor_ids: The IDs of the Sensors to fetch the last readings from.
    """
    return {
        sensor_id: get_sensor_last_reading_by_id(sensor_id)
        for sensor_id in sensor_ids
    }


def get_sensors_readings_counts_since_today_by_ids(
    sensor_ids: Iterable[int]
) -> dict[int, int]:
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


# -- users --

def get_users(
    updated_after: datetime | None = None
) -> tuple[dict[str, Any], ...]:
    """Return all users.

    If `updated_after` is given, return only users that were updated after the given
    date.
    """
    query =  db.select(
        User.id,
        User.display_name,
        User.username,
        User.avatar_colour,
        User.permissions,
        User.created_on,
        User.updated_on,
    )

    if updated_after:
        query = query.filter(
            User.updated_on > updated_after,
        )

    query = query.order_by(User.created_on.asc())

    users = db.session.execute(query)
    return _rows_to_dicts(users)


def get_user_by_id(id: int) -> User | None:
    """Return the User with the given id, or None."""
    user = db.session.execute(
        db.select(
            User
        ).where(
            User.id == id
        )
    ).scalar_one_or_none()

    return user


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


def get_admin() -> User | None:
    """Return the User with admin permissions, or None."""
    user = db.session.execute(
        db.select(
            User
        ).where(
            User.permissions == User.Permission.ADMIN.value
        )
    ).scalar_one_or_none()

    return user


def get_user_ids() -> Sequence[int]:
    """Return all user IDs."""
    result = db.session.execute(
        db.select(User.id)
    ).scalars().all()

    return result


def user_id_exists(user_id: int) -> bool:
    """Return whether a user with the given ID exists."""
    result = db.session.execute(
        db.select(
            db.exists().where(User.id == user_id)
        )
    ).scalar_one()

    return result


def create_user(
    display_name: str,
    username: str,
    password: str,
    is_password_temporary: bool,
    permissions: User.Permission,
    homepage: User.WebPage = User.WebPage.READINGS,
    temperature_unit: User.TemperatureUnit = User.TemperatureUnit.CELSIUS,
) -> User:
    """Create a user in the database.

    Args:
        display_name: The name others will see. Must be between User.MIN_NAME_LENGTH and
            User.MAX_NAME_LENGTH characters.
        username: The name used for logging in. Must be between User.MIN_NAME_LENGTH and
            User.MAX_NAME_LENGTH characters.
        password: The password. Must be between User.MIN_PASSWORD_LENGTH and
            User.MAX_PASSWORD_LENGTH characters.
        is_password_temporary: Whether the user must change this password after using
            it to log in (either for the first time, or after a password reset).
        permissions: The user's permissions.
        homepage: The page the user is redirected to after logging in.
        temperature_unit: The unit for displaying any temperatures.

    Returns:
        The newly created User object.
    """
    user = User(
        display_name,
        username,
        password,
        is_password_temporary,
        permissions,
        homepage,
        temperature_unit,
    )
    db.session.add(user)
    db.session.commit()

    return user


def update_user_by_id(
    user_id: int,
    display_name: str,
    username: str,
    permissions: User.Permission,
    homepage: User.WebPage,
    temperature_unit: User.TemperatureUnit
) -> None:
    """Update a user in the database.

    Args:
        user_id: The ID of the user.
        display_name: The name that others will see.
        username: The name used for logging in.
        permissions: The user's permissions.
        homepage: The first page the user sees after logging in.
        temperature_unit: The unit used to display temperatures.
    """
    db.session.execute(
        db.update(
            User
        ).where(
            User.id == user_id
        ).values(
            display_name=display_name,
            username=username,
            permissions=permissions.value,
            homepage=homepage,
            temperature_unit=temperature_unit,
            updated_on=datetime.utcnow()
        )
    )
    db.session.commit()

def update_user_permissions_by_id(
    user_id: int,
    permissions: User.Permission,
) -> None:
    """Update the given user's permissions.

    Args:
        user_id: The ID of the user.
        permissions: The new permissions.
    """
    db.session.execute(
        db.update(
            User
        ).where(
            User.id == user_id
        ).values(
            permissions=permissions.value,
            updated_on=datetime.utcnow()
        )
    )
    db.session.commit()


def update_user_password_by_id(
    user_id: int,
    password: str,
    is_temporary: bool
) -> None:
    """Update the given user's password.

    Args:
        user_id: The ID of the user.
        password: The new password.
        is_temporary: Whether the user must change this password after using it to log
            in (usually, after a password reset).
    """
    now = datetime.utcnow()
    db.session.execute(
        db.update(
            User
        ).where(
            User.id == user_id
        ).values(
            password_hash=User.generate_password_hash(password),
            is_password_temporary=is_temporary,
            password_changed_on=now,
            updated_on=now
        )
    )
    db.session.commit()


def get_user_last_password_change_time_by_id(user_id: int) -> datetime:
    """Return when the password of the User of id `user_id` was last changed."""
    result = db.session.execute(
        db.select(
            User.password_changed_on
        ).where(
            User.id == user_id
        )
    ).scalar_one()

    return result


def delete_user_by_id(user_id: int) -> None:
    """Delete the user with the given ID from the database."""
    db.session.execute(
        db.delete(
            User
        ).where(
            User.id == user_id
        )
    )
    db.session.commit()


def get_user_last_update_time(user_id: int) -> datetime:
    """Return when the User of id `user_id` was last updated."""
    result = db.session.execute(
        db.select(
            User.updated_on
        ).where(
            User.id == user_id
        )
    ).scalar_one()

    return result


def create_system_settings_timestamp_if_needed() -> None:
    """Create the system settings update timestamp if it does not exist."""
    already_exists = db.session.execute(
        db.select(
            db.exists().where(SystemSettingsTimestamp.id == 1)
        )
    ).scalar_one()

    if already_exists:
        return

    timestamp = SystemSettingsTimestamp(updated_on=datetime.utcnow())
    db.session.add(timestamp)
    current_app.logger.debug('creating missing system settings update timestamp.')


def _update_system_settings_timestamp() -> None:
    """Create or update the timestamp to mark the system settings as recently updated.

    A timestamp must already exist. Must commit the transaction after.
    """
    db.session.execute(
        db.update(
            SystemSettingsTimestamp
        ).where(
            SystemSettingsTimestamp.id == 1
        ).values(
            updated_on=datetime.utcnow()
        )
    )


def get_system_settings_update_timestamp() -> datetime:
    """Return when the system settings were last updated."""
    result = db.session.execute(
        db.select(
            SystemSettingsTimestamp.updated_on
        ).where(
            SystemSettingsTimestamp.id == 1
        )
    ).scalar_one()

    return result


def create_missing_system_settings() -> None:
    """Create any missing system settings with default values."""
    all_stored_keys = db.session.execute(
        db.select(
            SystemSetting.key
        )
    ).scalars().all()

    to_be_created = {}

    for key in default_system_settings_base:
        if key not in all_stored_keys:
            to_be_created[key] = default_system_settings_base[key]['value']

    for key in to_be_created:
        default_value = to_be_created[key]
        setting = SystemSetting(key=key, value=default_value)
        db.session.add(setting)
        current_app.logger.debug(f'creating missing SystemSetting "{key}"')

    if to_be_created:
        # something was created. must update the timestamp
        _update_system_settings_timestamp()

    db.session.commit()


def update_system_settings(updated_settings: dict[str, str]) -> None:
    """Update system settings.

    Args:
        updated_settings: A dict of system settings with updated values.
    """
    for key in updated_settings:
        updated_value = updated_settings[key]
        db.session.execute(
            db.update(
                SystemSetting
            ).where(
                SystemSetting.key == key
            ).values(
                value=updated_value,
            )
        )
    _update_system_settings_timestamp()

    db.session.commit()


def get_system_settings() -> dict[str, str]:
    """Get all system settings as a dict."""
    result = db.session.execute(
        db.select(
            SystemSetting.key,
            SystemSetting.value,
        )
    ).all()

    return {key: value for (key, value) in result}
