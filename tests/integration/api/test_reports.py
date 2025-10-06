from datetime import datetime
from os import path
import re

from flask_login import current_user

from app.extensions import db
from app.models.readings import Sensor, Reading
from app.models.users import User
from app.api.report import (
    generate_report_code, store_report_file, get_report_file, format_report_code,
    MAX_NOTES_LENGTH,
)


report_code_pattern = re.compile(r'[a-z0-9]{10}')

def test_generate_report_code_format():
    assert report_code_pattern.match(generate_report_code())


def test_store_report_file_writes_file(app, tmp_path):
    report_code = 'abcde12345'
    content = 'This is a test.\n'
    app.config['REPORTS_DIRECTORY'] = tmp_path
    with app.app_context():
        store_report_file(report_code, content)
        with open(path.join(tmp_path, f'{report_code}.html')) as report_file:
            assert report_file.read() == content


def test_get_report_file(app, tmp_path):
    report_code = 'abcde12345'
    content = 'This is a test.\n'
    with open(path.join(tmp_path, f'{report_code}.html'), 'w') as report_file:
        report_file.write(content)

    app.config['REPORTS_DIRECTORY'] = tmp_path
    with app.app_context():
        assert get_report_file(report_code) == content


def test_format_report_code_format():
    assert format_report_code('abcde12345') == 'ABCD-E123-45'


def test_create_report_writes_table_report(
    app, sensor: Sensor, logged_in_admin_client, tmp_path, default_system_settings
):
    with app.app_context():
        for reading in (
            Reading(sensor.id, 10.0, datetime(2025, 10, 1, 1)),
            Reading(sensor.id, 11.0, datetime(2025, 10, 1, 2)),
            Reading(sensor.id, 12.0, datetime(2025, 10, 1, 3)),
            Reading(sensor.id, 13.0, datetime(1, 1, 1))
        ):
            db.session.add(reading)
        db.session.commit()

        app.config['REPORTS_DIRECTORY'] = tmp_path
        response = logged_in_admin_client.post('/api/reports', json={
            'sensor_id': sensor.id,
            'range_start': '2025-10-01T00:00:00.000Z',
            'range_end':   '2025-10-01T23:59:59.999Z',
            'data_format': 'table',
            'notes': None
        })
        assert response.status_code == 200
        returned_code = response.json
        assert report_code_pattern.match(returned_code)

        with open(path.join(tmp_path, f'{returned_code}.html')) as report_file:
            # reading it into a string as the HTML itself is not terribly large
            html = report_file.read()
            assert 'tables-section' in html
            assert 'graph-section' not in html

def test_create_report_writes_graph_report(
    app, sensor: Sensor, logged_in_admin_client, tmp_path, default_system_settings
):
    with app.app_context():
        for reading in (
            Reading(sensor.id, 10.0, datetime(2025, 10, 1, 1)),
            Reading(sensor.id, 11.0, datetime(2025, 10, 1, 2)),
            Reading(sensor.id, 12.0, datetime(2025, 10, 1, 3)),
            Reading(sensor.id, 13.0, datetime(1, 1, 1))
        ):
            db.session.add(reading)
        db.session.commit()

        app.config['REPORTS_DIRECTORY'] = tmp_path
        response = logged_in_admin_client.post('/api/reports', json={
            'sensor_id': sensor.id,
            'range_start': '2025-10-01T00:00:00.000Z',
            'range_end':   '2025-10-01T23:59:59.999Z',
            'data_format': 'graph',
            'notes': None
        })
        assert response.status_code == 200
        returned_code = response.json
        assert report_code_pattern.match(returned_code)

        with open(path.join(tmp_path, f'{returned_code}.html')) as report_file:
            html = report_file.read()
            assert 'tables-section' not in html
            assert 'graph-section' in html

def test_create_report_writes_table_and_graph_report(
    app, sensor: Sensor, logged_in_admin_client, tmp_path, default_system_settings
):
    with app.app_context():
        for reading in (
            Reading(sensor.id, 10.0, datetime(2025, 10, 1, 1)),
            Reading(sensor.id, 11.0, datetime(2025, 10, 1, 2)),
            Reading(sensor.id, 12.0, datetime(2025, 10, 1, 3)),
            Reading(sensor.id, 13.0, datetime(1, 1, 1))
        ):
            db.session.add(reading)
        db.session.commit()

        app.config['REPORTS_DIRECTORY'] = tmp_path
        response = logged_in_admin_client.post('/api/reports', json={
            'sensor_id': sensor.id,
            'range_start': '2025-10-01T00:00:00.000Z',
            'range_end':   '2025-10-01T23:59:59.999Z',
            'data_format': 'table-and-graph',
            'notes': None
        })
        assert response.status_code == 200
        returned_code = response.json
        assert report_code_pattern.match(returned_code)

        with open(path.join(tmp_path, f'{returned_code}.html')) as report_file:
            html = report_file.read()
            assert 'tables-section' in html
            assert 'graph-section' in html

def test_create_report_writes_empty_report(
    app, sensor: Sensor, logged_in_admin_client, tmp_path, default_system_settings
):
    app.config['REPORTS_DIRECTORY'] = tmp_path
    response = logged_in_admin_client.post('/api/reports', json={
        'sensor_id': sensor.id,
        'range_start': '2025-10-01T00:00:00.000Z',
        'range_end':   '2025-10-01T23:59:59.999Z',
        'data_format': 'table',
        'notes': None
    })
    assert response.status_code == 200
    returned_code = response.json
    assert report_code_pattern.match(returned_code)

    with open(path.join(tmp_path, f'{returned_code}.html')) as report_file:
        html = report_file.read()
        assert 'No readings in the given time frame.' in html
        assert 'tables-section' not in html
        assert 'graph-section' not in html

def test_create_report_writes_notes(
    app, sensor: Sensor, logged_in_admin_client, tmp_path, default_system_settings
):
    app.config['REPORTS_DIRECTORY'] = tmp_path
    response = logged_in_admin_client.post('/api/reports', json={
        'sensor_id': sensor.id,
        'range_start': '2025-10-01T00:00:00.000Z',
        'range_end':   '2025-10-01T23:59:59.999Z',
        'data_format': 'table',
        'notes': 'This is a test report.'
    })
    assert response.status_code == 200
    returned_code = response.json
    assert report_code_pattern.match(returned_code)

    with open(path.join(tmp_path, f'{returned_code}.html')) as report_file:
        html = report_file.read()
        assert 'This is a test report.' in html

def test_create_report_unknown_sensor(
    app, logged_in_admin_client, tmp_path, default_system_settings
):
    app.config['REPORTS_DIRECTORY'] = tmp_path
    response = logged_in_admin_client.post('/api/reports', json={
        'sensor_id': 123,
        'range_start': '2025-10-01T00:00:00.000Z',
        'range_end':   '2025-10-01T23:59:59.999Z',
        'data_format': 'table',
        'notes': None
    })
    assert response.status_code == 404
    assert response.json['error'] == 'unknown_sensor'

def test_create_report_obeys_fahrenheit_temperature_unit(
    app, sensor: Sensor, logged_in_admin_client, tmp_path, default_system_settings
):
    app.config['REPORTS_DIRECTORY'] = tmp_path
    with logged_in_admin_client:
        logged_in_admin_client.get('/')  # just to initialise current_user
        current_user.temperature_unit = User.TemperatureUnit.FAHRENHEIT
    response = logged_in_admin_client.post('/api/reports', json={
        'sensor_id': sensor.id,
        'range_start': '2025-10-01T00:00:00.000Z',
        'range_end':   '2025-10-01T23:59:59.999Z',
        'data_format': 'table',
        'notes': None
    })
    assert response.status_code == 200
    returned_code = response.json
    assert report_code_pattern.match(returned_code)

    with open(path.join(tmp_path, f'{returned_code}.html')) as report_file:
        html = report_file.read()
        assert 'Celsius (°C)' not in html
        assert 'Fahrenheit (°F)' in html

def test_create_report_invalid_fields(
    app, sensor: Sensor, logged_in_admin_client, tmp_path, default_system_settings
):
    app.config['REPORTS_DIRECTORY'] = tmp_path
    response = logged_in_admin_client.post('/api/reports', json={
        'wrong': 123,
    })
    assert response.status_code == 400
    assert response.json['error'] == 'field_error'

def test_create_report_invalid_timeframe(
    app, sensor: Sensor, logged_in_admin_client, tmp_path, default_system_settings
):
    app.config['REPORTS_DIRECTORY'] = tmp_path
    response = logged_in_admin_client.post('/api/reports', json={
        'sensor_id': 123,
        'range_start': '2025-10-01T00:00:00.000Z',
        'range_end':   '2025-09-01T23:59:59.999Z',  # a month before range_start
        'data_format': 'table',
        'notes': None
    })
    assert response.status_code == 400
    assert response.json['error'] == 'invalid_range'

def test_create_report_invalid_too_long_notes(
    app, sensor: Sensor, logged_in_admin_client, tmp_path, default_system_settings
):
    app.config['REPORTS_DIRECTORY'] = tmp_path
    response = logged_in_admin_client.post('/api/reports', json={
        'sensor_id': 123,
        'range_start': '2025-10-01T00:00:00.000Z',
        'range_end':   '2025-10-01T23:59:59.999Z',
        'data_format': 'table',
        'notes': 'a' * (MAX_NOTES_LENGTH+1)
    })
    assert response.status_code == 400
    assert response.json['error'] == 'invalid_notes_length'
