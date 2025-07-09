from flask import jsonify, request

from app.api import bp
from app.dbapi import (
    get_sensors, get_sensor_ids,
    create_sensor,
    get_latest_readings_from_sensors, get_today_readings_count_from_sensors,
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


# TODO: sensor 'ping' route. requires sensor key too

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
        'created_on': reading['temperature'],
    }), 201


@bp.route('/sensors/readings-count/today')
def api_sensors_today_readings_count():
    sensor_ids = get_sensor_ids()
    return get_today_readings_count_from_sensors(sensor_ids)


def _parse_sensor_ids(raw_sensor_ids: str) -> list[str]:
    """Parse a comma-separated list of sensor IDs into a list."""
    parsed = []
    for raw_sensor_id in raw_sensor_ids.split(','):
        sensor_id = int(raw_sensor_id)
        # ignore duplicates
        if sensor_id not in parsed:
            parsed.append(sensor_id)

    return parsed

# TODO: extract this to a configurable option in the interface
_READINGS_LIMIT = 40

@bp.route('/readings/latest')
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

    latest_readings = get_latest_readings_from_sensors(
        sensor_ids, _READINGS_LIMIT
    )
    return jsonify(latest_readings)
