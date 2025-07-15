from datetime import datetime

from flask import jsonify, request

from app.api import bp
from app.dbapi import (
    get_sensors, get_sensor_ids,
    create_sensor,
    get_sensors_last_readings,
    get_sensors_latest_readings, get_sensors_readings_counts_since_today,
    get_sensor_readings_count_in_time_range,
    create_reading
)


@bp.route('/sensors', methods=['GET', 'POST'])
def api_sensors():
    if request.method == 'GET':
        sensors = get_sensors()
        return jsonify(sensors)

    try:
        name = request.json['name']
    except KeyError:
        return jsonify({'error': 'field_error'}), 400

    # TODO: check name length
    # TODO: check if name already exists

    sensor = create_sensor(name)

    return jsonify({
        'id': sensor['id'],
        'name': sensor['name'],
        'created_on': sensor['created_on'],
    }), 201


@bp.route('/sensors/last-readings')
def api_last_readings():
    sensor_ids = get_sensor_ids()

    last_readings = get_sensors_last_readings(sensor_ids)
    return jsonify(last_readings)


# TODO: extract this to a configurable option in the interface
_READINGS_LIMIT = 40

@bp.route('/sensors/latest-readings')
def api_latest_readings():
    raw_sensor_ids = request.args.get('sensor_ids')
    sensor_ids = None
    if not raw_sensor_ids:
        sensor_ids = get_sensor_ids()
    else:
        try:
            sensor_ids = _parse_sensor_ids(raw_sensor_ids)
            # TODO: verify if each one exists?
        except (ValueError, TypeError):
            return jsonify({'error': 'field_error'}), 400

    latest_readings = get_sensors_latest_readings(
        sensor_ids, _READINGS_LIMIT
    )
    return jsonify(latest_readings)


@bp.route('/sensors/<int:sensor_id>/readings', methods=['POST'])
def api_sensor_readings(sensor_id):
    try:
        temperature = float(request.json['temperature'])
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'field_error'}), 400

    # TODO: throw error if sensor_id doesn't exist
    reading = create_reading(sensor_id, temperature)

    return jsonify({
        'id': reading['id'],
        'sensor_id': reading['sensor_id'],
        'temperature': reading['temperature'],
        'created_on': reading['created_on'],
    }), 201


# TODO: sensor 'ping' route. requires sensor key too
def _parse_iso_datetime(iso_datetime: str) -> datetime:
    """Return the given datetime string as a datetime object.

    Args:
        iso_datetime: ISO datetime string according to the JavaScript datetime
            format, 'YYYY-MM-DDThh:mm:ss.sssZ'.
    """
    return datetime.strptime(iso_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')

@bp.route('/sensors/<int:sensor_id>/readings-count')
def api_sensor_readings_count(sensor_id):
    try:
        range_start = _parse_iso_datetime(request.args['range_start'])
        range_end = _parse_iso_datetime(request.args['range_end'])
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'field_error'}), 400

    readings = get_sensor_readings_count_in_time_range(
        sensor_id, range_start, range_end
    )

    return jsonify(readings)


@bp.route('/sensors/readings-count/today')
def api_sensors_today_readings_count():
    sensor_ids = get_sensor_ids()
    return jsonify(
        get_sensors_readings_counts_since_today(sensor_ids)
    )


def _parse_sensor_ids(raw_sensor_ids: str) -> list[str]:
    """Parse a comma-separated list of sensor IDs into a list."""
    parsed = []
    for raw_sensor_id in raw_sensor_ids.split(','):
        sensor_id = int(raw_sensor_id)
        # ignore duplicates
        if sensor_id not in parsed:
            parsed.append(sensor_id)

    return parsed
