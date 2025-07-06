from flask import jsonify, request

from app.api import bp
from app.dbapi import (
    get_sensors,
    create_sensor,
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


@bp.route('/readings', methods=['GET', 'POST'])
def api_readings():
    if request.method == 'GET':
        # TODO
        return jsonify('TODO')

    try:
        sensor_id = int(request.json['sensor_id'])
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
