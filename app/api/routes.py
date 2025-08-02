from datetime import datetime, timedelta

from flask import jsonify, request

from app.api import bp
from app.dbapi import (
    get_sensors, get_sensor_ids, get_sensor_name, sensor_name_exists,
    create_sensor,
    get_sensors_last_readings,
    get_sensors_readings_counts_since_today,
    get_sensor_readings_in_time_range,
    get_sensors_readings_in_time_ranges, get_sensor_readings_count_in_time_range,
    create_reading,
)
from app.api.report import (
    DataFormat,
    generate_token,
    generate_report_html,
    store_report_file
)
from app.models.readings import Sensor


@bp.route('/sensors', methods=['GET', 'POST'])
def api_sensors():
    if request.method == 'GET':
        sensors = get_sensors()
        return jsonify(sensors)

    try:
        name = str(request.json['name']).strip()
    except KeyError:
        return jsonify({'error': 'field_error'}), 400

    name_length = len(name)
    if (
        name_length < Sensor.MIN_NAME_LENGTH
        or name_length > Sensor.MAX_NAME_LENGTH
    ):
        return jsonify({'error': 'invalid_name_length'}), 400

    if sensor_name_exists(name):
        return jsonify({'error': 'name_already_exists'}), 400

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


def _parse_iso_datetimes(iso_datetimes: str) -> list[datetime]:
    """Return the given comma-separated datetimes string as a list of datetime objects.

    Args:
        iso_datetimes: comma-separated string of ISO datetime strings, each one in the
            format of 'YYYY-MM-DDThh:mm:ss.sssZ'.
    """
    parsed = []
    for iso_datetime in iso_datetimes.split(','):
        parsed.append(_parse_iso_datetime(iso_datetime))

    return parsed


@bp.route('/sensors/readings')
def api_readings_by_days():
    try:
        start_datetimes = _parse_iso_datetimes(request.args['start_dates'])
        sensor_ids = _parse_ints(request.args['sensor_ids'], True)
    except (ValueError, TypeError):
        return jsonify({'error': 'field_error'}), 400

    offset_ids = None
    raw_offset_ids = request.args.get('offset_ids')
    if raw_offset_ids:
        try:
            offset_ids = _parse_ints(raw_offset_ids)
        except (ValueError, TypeError):
            return jsonify({'error': 'field_error'}), 400

    time_ranges = []
    for start_of_day in start_datetimes:
        end_of_day = (
            start_of_day
            + timedelta(hours=23, minutes=59, seconds=59, milliseconds=9999)
        )
        time_ranges.append({'start': start_of_day, 'end': end_of_day})

    readings_for_day = get_sensors_readings_in_time_ranges(
        sensor_ids, offset_ids, time_ranges
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


def _parse_ints(raw_ints: str, ignore_duplicates: bool = False) -> list[int]:
    """Parse a comma-separated string of integers into a list of ints.

    Args:
        raw_ints: The string of ints to parse.
        unique_only: When True, duplicates are ignored.
    """
    parsed = []
    for integer in raw_ints.split(','):
        integer = int(integer)
        # ignore duplicates
        if not ignore_duplicates or integer not in parsed:
            parsed.append(integer)

    return parsed


@bp.route('/reports', methods=['POST'])
def api_generate_report():
    try:
        sensor_id = int(request.json['sensor_id'])
        range_start = _parse_iso_datetime(request.json['range_start'])
        range_end = _parse_iso_datetime(request.json['range_end'])
        data_format = DataFormat(request.json['data_format'])
        notes = request.json['notes']
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'field_error'}), 400

    # TODO: verify sensor's existence
    # TODO: verify that range_start < range_end

    if notes:
        notes = notes.strip() or None

    # TODO: verify notes length

    sensor_name = get_sensor_name(sensor_id)
    readings = get_sensor_readings_in_time_range(
        sensor_id, None, range_start, range_end
    )

    # TODO: verify readings count
    #
    token = generate_token()
    utc_now = datetime.utcnow()

    report_html = generate_report_html(
        sensor_name,
        token,
        utc_now,
        range_start,
        range_end,
        readings,
        data_format,
        notes
    )
    store_report_file(token, report_html)
    return jsonify(token)
