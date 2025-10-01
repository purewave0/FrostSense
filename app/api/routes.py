import datetime as dt

from flask import jsonify, request, abort
from flask_login import current_user, login_user, login_required, logout_user

from app.api import bp
from app.dbapi import (
    get_sensors, get_sensor_ids, get_sensor_by_id, sensor_name_exists,
    sensor_id_exists, get_sensor_key_by_id,
    update_sensor_by_id,
    get_sensors_last_readings,
    get_sensors_readings_counts_since_today,
    get_sensor_readings_in_time_range,
    get_sensors_readings_in_time_ranges, get_sensor_readings_count_in_time_range,
    create_reading,
    get_users, get_user_by_id, get_user_by_username,
    user_id_exists,
    create_user, update_user_by_id, delete_user_by_id,
    update_user_password_by_id, get_user_last_password_change_time,
    get_user_last_update_time,
    get_system_settings,
    update_system_settings, get_system_settings_update_timestamp
)
from app.api.report import (
    DataFormat,
    generate_report_code,
    generate_report_html,
    store_report_file,
    MAX_NOTES_LENGTH
)
from app.models.readings import Sensor
from app.models.users import User
from app.models.system_settings import defaultSystemSettings
from app.util import permission_required, login_and_permanent_password_required


@bp.route('/sensors')
@login_and_permanent_password_required
def api_sensors():
    sensors = get_sensors()
    return jsonify(sensors)


@bp.route('/sensors/last-readings')
@login_and_permanent_password_required
def api_last_readings():
    sensor_ids = get_sensor_ids()

    last_readings = get_sensors_last_readings(sensor_ids)
    return jsonify(last_readings)


def _parse_iso_datetimes(iso_datetimes: str) -> list[dt.datetime]:
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
@login_and_permanent_password_required
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
            + dt.timedelta(hours=23, minutes=59, seconds=59, milliseconds=9999)
        )
        time_ranges.append({'start': start_of_day, 'end': end_of_day})

    readings_for_day = get_sensors_readings_in_time_ranges(
        sensor_ids, offset_ids, time_ranges
    )
    return jsonify(readings_for_day)


@bp.route('/sensors/<int:sensor_id>/readings', methods=['POST'])
@login_and_permanent_password_required
def api_sensor_readings(sensor_id):
    try:
        temperature = float(request.json['temperature'])
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'field_error'}), 400

    try:
        given_key = str(request.headers['Authorization'])
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'authorization_missing'}), 401

    sensor_key = get_sensor_key_by_id(sensor_id)
    if not sensor_key:
        return jsonify({'error': 'unknown_sensor'}), 404
    if sensor_key != given_key:
        return jsonify({'error': 'incorrect_key'}), 401

    reading = create_reading(sensor_id, temperature)

    return jsonify({
        'id': reading['id'],
        'sensor_id': reading['sensor_id'],
        'temperature': reading['temperature'],
        'created_on': reading['created_on'],
    }), 201


def _parse_iso_datetime(iso_datetime: str) -> dt.datetime:
    """Return the given datetime string as a datetime object.

    Args:
        iso_datetime: ISO datetime string according to the JavaScript datetime
            format, 'YYYY-MM-DDThh:mm:ss.sssZ'.
    """
    return dt.datetime.strptime(iso_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')

@bp.route('/sensors/<int:sensor_id>/readings-count')
@login_and_permanent_password_required
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
@login_and_permanent_password_required
def api_sensors_today_readings_count():
    sensor_ids = get_sensor_ids()
    return jsonify(
        get_sensors_readings_counts_since_today(sensor_ids)
    )


@bp.route('/sensors/<int:sensor_id>', methods=['PUT'])
@login_and_permanent_password_required
@permission_required(User.Permission.EDIT_SENSORS)
def api_update_sensor(sensor_id):
    try:
        name = str(request.json['name']).strip()
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'field_error'}), 400

    if not sensor_id_exists(sensor_id):
        return jsonify({'error': 'unknown_sensor'}), 404

    name_length = len(name)
    if (
        name_length < Sensor.MIN_NAME_LENGTH
        or name_length > Sensor.MAX_NAME_LENGTH
    ):
        return jsonify({'error': 'invalid_name_length'}), 400

    if sensor_name_exists(name):
        return jsonify({'error': 'name_already_exists'}), 400

    update_sensor_by_id(sensor_id, name)
    return '', 204


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
@login_and_permanent_password_required
@permission_required(User.Permission.MANAGE_REPORTS)
def api_generate_report():
    try:
        sensor_id = int(request.json['sensor_id'])
        range_start = _parse_iso_datetime(request.json['range_start'])
        range_end = _parse_iso_datetime(request.json['range_end'])
        data_format = DataFormat(request.json['data_format'])
        notes = request.json['notes']
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'field_error'}), 400


    if notes:
        notes = notes.strip() or None
        if notes and len(notes) > MAX_NOTES_LENGTH:
            return jsonify({'error': 'invalid_notes_length'}), 400


    if not (range_start < range_end):
        return jsonify({'error': 'invalid_range'}), 400

    sensor = get_sensor_by_id(sensor_id)
    if not sensor:
        return jsonify({'error': 'unknown_sensor'}), 404

    readings = get_sensor_readings_in_time_range(
        sensor_id, None, range_start, range_end
    )

    code = generate_report_code()
    utc_now = dt.datetime.now(dt.timezone.utc)

    system_settings = get_system_settings()

    report_html = generate_report_html(
        sensor.name,
        code,
        utc_now,
        range_start,
        range_end,
        current_user.temperature_unit,
        current_user.display_name,
        float(system_settings['minimum_graph_value']),
        float(system_settings['maximum_graph_value']),
        readings,
        data_format,
        notes
    )
    store_report_file(code, report_html)
    return jsonify(code)


# -- auth --

@bp.route('/login', methods=['POST'])
def api_login():
    try:
        username = str(request.json['username'])
        password = str(request.json['password'])
        should_remember_login = bool(request.json['remember_login'])
    except KeyError:
        return jsonify({'error': 'field_error'}), 400

    username_length = len(username)
    password_length = len(password)
    if (
        username_length < User.MIN_NAME_LENGTH
        or username_length > User.MAX_NAME_LENGTH
        or password_length < User.MIN_PASSWORD_LENGTH
        or password_length > User.MAX_PASSWORD_LENGTH
    ):
        return jsonify({'error': 'incorrect_login'}), 401

    if current_user.is_authenticated:
        # already logged in
        return '', 204

    user = get_user_by_username(username)
    if user is None or not user.check_password(password):
        return jsonify({'error': 'incorrect_login'}), 401

    login_user(user, remember=should_remember_login)
    return '', 204


@bp.route('/me/permanent-password', methods=['POST'])
@login_required
def api_create_permanent_password():
    try:
        password = str(request.json['password'])
    except KeyError:
        return jsonify({'error': 'field_error'}), 400

    password_length = len(password)
    if (
        password_length < User.MIN_PASSWORD_LENGTH
        or password_length > User.MAX_PASSWORD_LENGTH
    ):
        return jsonify({'error': 'invalid_password_length'}), 400

    if not current_user.is_password_temporary:
        return jsonify({'error': 'password_already_permanent'}), 409

    if current_user.check_password(password):
        return jsonify({'error': 'same_as_temporary'}), 400

    update_user_password_by_id(current_user.id, password, False)

    return '', 204


@bp.route('/me/password', methods=['PUT'])
@login_and_permanent_password_required
def api_change_password():
    try:
        current_password = str(request.json['current_password'])
        new_password = str(request.json['password'])
    except KeyError:
        return jsonify({'error': 'field_error'}), 400

    if not current_user.check_password(current_password):
        return jsonify({'error': 'incorrect_current_password'}), 401

    password_length = len(new_password)
    if (
        password_length < User.MIN_PASSWORD_LENGTH
        or password_length > User.MAX_PASSWORD_LENGTH
    ):
        return jsonify({'error': 'invalid_password_length'}), 400

    update_user_password_by_id(current_user.id, new_password, False)

    return '', 204


@bp.route('/me/last-password-change-time')
@login_and_permanent_password_required
def api_password_changed_on():
    password_changed_on = get_user_last_password_change_time(current_user.id)
    return jsonify(password_changed_on)


@bp.route('/me/preferences', methods=['GET', 'PUT'])
@login_and_permanent_password_required
def api_own_preferences():
    if request.method == 'GET':
        user = get_user_by_id(current_user.id)
        if not user:
            return jsonify({'error': 'user_not_found'}), 404
        return jsonify({
            'display_name': user.display_name,
            'username': user.username,
            'homepage': user.homepage,
            'temperature_unit': user.temperature_unit,
        })

    try:
        display_name = str(request.json['display_name']).strip()
        username = str(request.json['username']).strip()
        homepage = User.WebPage(request.json['homepage'])
        temperature_unit = User.TemperatureUnit(request.json['temperature_unit'])
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'field_error'}), 400

    username_length = len(username)
    if (
        username_length < User.MIN_NAME_LENGTH
        or username_length > User.MAX_NAME_LENGTH
    ):
        return jsonify({'error': 'invalid_username'}), 400

    if any(char.isspace() for char in username):
        return jsonify({'error': 'invalid_username'}), 400

    if username != current_user.username and get_user_by_username(username):
        return jsonify({'error': 'username_already_exists'}), 400

    final_display_name = None
    # the admin is the only one who can edit their own Display Name. for other users,
    # the received value for this field is just ignored
    if not current_user.has_permission(User.Permission.ADMIN):
        final_display_name = current_user.display_name
    else:
        display_name_length = len(display_name)
        if (
            display_name_length < User.MIN_NAME_LENGTH
            or display_name_length > User.MAX_NAME_LENGTH
        ):
            return jsonify({'error': 'invalid_display_name'}), 400

        final_display_name = display_name

    update_user_by_id(
        current_user.id,
        final_display_name,
        username,
        User.Permission(current_user.permissions),
        homepage,
        temperature_unit
    )
    return '', 204


@bp.route('/me/preferences/last-update-time')
@login_and_permanent_password_required
def api_own_preferences_timestamp():
    return jsonify(get_user_last_update_time(current_user.id))


@bp.route('/logout')
@login_required
def api_logout():
    logout_user()
    return '', 204


# -- users --

@bp.route('/users', methods=['GET', 'POST'])
@login_and_permanent_password_required
@permission_required(User.Permission.MANAGE_USERS)
def api_users():
    if request.method == 'GET':
        users = get_users()
        return jsonify(users)

    try:
        display_name = str(request.json['display_name']).strip()
        username = str(request.json['username']).strip()
        raw_permissions = int(request.json['permissions'])
        if raw_permissions < 0:
            raise ValueError('negative permission')
        permissions = User.Permission(raw_permissions)
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'field_error'}), 400

    contains_illegal_permission = (
        User.Permission.ASSIGNABLE_PERMISSIONS & permissions != permissions
    )
    if contains_illegal_permission:
        return jsonify({'error': 'illegal_permission'}), 400

    display_name_length = len(display_name)
    if (
        display_name_length < User.MIN_NAME_LENGTH
        or display_name_length > User.MAX_NAME_LENGTH
    ):
        return jsonify({'error': 'invalid_display_name'}), 400

    username_length = len(username)
    if (
        username_length < User.MIN_NAME_LENGTH
        or username_length > User.MAX_NAME_LENGTH
    ):
        return jsonify({'error': 'invalid_username'}), 400

    if any(char.isspace() for char in username):
        return jsonify({'error': 'invalid_username'}), 400

    if get_user_by_username(username):
        return jsonify({'error': 'username_already_exists'}), 400

    temporary_password = User.generate_temporary_password()
    system_settings = get_system_settings()
    default_temperature_unit = User.TemperatureUnit(
        system_settings['default_temperature_unit']
    )
    new_user = create_user(
        display_name,
        username,
        temporary_password,
        True,
        permissions,
        User.WebPage.READINGS,
        default_temperature_unit
    )

    return jsonify({
        'id':                 new_user.id,
        'display_name':       new_user.display_name,
        'username':           new_user.username,
        'temporary_password': temporary_password,
        'permissions':        new_user.permissions,
        'created_on':         new_user.created_on,
        'updated_on':         new_user.updated_on,
    }), 201


@bp.route('/users/summary')
@login_and_permanent_password_required
@permission_required(User.Permission.MANAGE_USERS)
def api_users_summary():
    try:
        updated_after = _parse_iso_datetime(request.args.get('updated-after'))
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'invalid_datetime'}), 400

    updated_users = []
    user_ids = []
    users = get_users()
    for user in users:
        user_ids.append(user['id'])
        if user['updated_on'] > updated_after:
            updated_users.append(user)

    return jsonify(
        {'updated_users': updated_users, 'all_user_ids': user_ids }
    )


@bp.route('/users/<int:user_id>', methods=['PUT', 'DELETE'])
@login_and_permanent_password_required
@permission_required(User.Permission.MANAGE_USERS)
def api_update_user(user_id: int):
    if request.method == 'DELETE':
        delete_user_by_id(user_id)
        return '', 204

    try:
        display_name = str(request.json['display_name']).strip()
        raw_permissions = int(request.json['permissions'])
        if raw_permissions < 0:
            raise ValueError('negative permission')
        permissions = User.Permission(raw_permissions)
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'field_error'}), 400

    display_name_length = len(display_name)
    if (
        display_name_length < User.MIN_NAME_LENGTH
        or display_name_length > User.MAX_NAME_LENGTH
    ):
        return jsonify({'error': 'invalid_display_name'}), 400

    contains_illegal_permission = (
        User.Permission.ASSIGNABLE_PERMISSIONS & permissions != permissions
    )
    if contains_illegal_permission:
        return jsonify({'error': 'illegal_permission'}), 400

    if user_id == current_user.id:
        return jsonify({'error': 'editing_yourself'}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'user_not_found'}), 404

    update_user_by_id(
        user_id,
        display_name,
        user.username,
        permissions,
        user.homepage,
        user.temperature_unit
    )
    return '', 204


@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_and_permanent_password_required
@permission_required(User.Permission.MANAGE_USERS)
def api_user_reset_password(user_id: int):
    if user_id == current_user.id:
        return jsonify({'error': 'editing_yourself'}), 400

    if not user_id_exists(user_id):
        return jsonify({'error': 'user_not_found'}), 404

    temporary_password = User.generate_temporary_password()
    update_user_password_by_id(user_id, temporary_password, True)

    return jsonify(temporary_password)


# -- system settings --

@bp.route('/system-settings', methods=['GET', 'PUT'])
@login_and_permanent_password_required
def api_system_settings():
    if request.method == 'GET':
        return get_system_settings()

    if not current_user.has_permission(User.Permission.MANAGE_SYSTEM_SETTINGS):
        return abort(403)

    try:
        default_temperature_unit = User.TemperatureUnit(
            request.json['default_temperature_unit']
        )
        minimum_gauge_value = int(request.json['minimum_gauge_value'])
        maximum_gauge_value = int(request.json['maximum_gauge_value'])
        minimum_graph_value = int(request.json['minimum_graph_value'])
        maximum_graph_value = int(request.json['maximum_graph_value'])
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'field_error'}), 400

    if (
        minimum_gauge_value < defaultSystemSettings['minimum_gauge_value']['min']
        or minimum_gauge_value > defaultSystemSettings['minimum_gauge_value']['max']
        or minimum_graph_value < defaultSystemSettings['minimum_graph_value']['min']
        or minimum_graph_value > defaultSystemSettings['minimum_graph_value']['max']
    ):
        return jsonify({'error': 'value_limits'}), 400

    update_system_settings({
        'default_temperature_unit': default_temperature_unit.value,
        'minimum_gauge_value': str(minimum_gauge_value),
        'maximum_gauge_value': str(maximum_gauge_value),
        'minimum_graph_value': str(minimum_graph_value),
        'maximum_graph_value': str(maximum_graph_value)
    })
    return '', 204


@bp.route('/system-settings/last-update-time')
@login_and_permanent_password_required
def api_system_settings_timestamp():
    return jsonify(get_system_settings_update_timestamp())
