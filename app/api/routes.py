from datetime import datetime, timedelta

from flask import jsonify, request

from app.api import bp
from app.dbapi import (
    get_sensors, get_sensor_ids,
    create_sensor,
    get_sensors_last_readings,
    get_sensors_readings_counts_since_today,
    get_sensors_readings_in_time_range, get_sensor_readings_count_in_time_range,
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


@bp.route('/sensors/readings/day/<start_of_day>')
def api_readings_for_day(start_of_day: str):
    try:
        start_datetime = _parse_iso_datetime(start_of_day)
    except (ValueError, TypeError):
        return jsonify({'error': 'field_error'}), 400

    raw_sensor_ids = request.args.get('sensor_ids')
    sensor_ids = None
    offset_ids = None
    if raw_sensor_ids:
        try:
            sensor_ids = _parse_ints(raw_sensor_ids)
        except (ValueError, TypeError):
            return jsonify({'error': 'field_error'}), 400

        # we accept offsets only when there are sensor ids, as that's what we link the
        # offsets to.
        raw_offset_ids = request.args.get('offset_ids')
        if raw_offset_ids:
            try:
                offset_ids = _parse_ints(raw_offset_ids)
            except (ValueError, TypeError):
                return jsonify({'error': 'field_error'}), 400
    else:
        sensor_ids = get_sensor_ids()

    end_of_day = (
        start_datetime
        + timedelta(hours=23, minutes=59, seconds=59, milliseconds=9999)
    )

    readings_for_day = get_sensors_readings_in_time_range(
        sensor_ids, offset_ids, start_datetime, end_of_day
    )
    return jsonify(readings_for_day)


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


def _parse_ints(raw_ints: str) -> list[int]:
    """Parse a comma-separated string of integers into a list of unique ints."""
    parsed = []
    for integer in raw_ints.split(','):
        integer = int(integer)
        # ignore duplicates
        if integer not in parsed:
            parsed.append(integer)

    return parsed
