from flask_login import current_user

from app.models.users import User


# auth

def test_login_success(client, user: User):
    with client:
        response = client.post('/api/login', json={
            'username': user.username,
            'password': 'password1',
            'remember_login': False,
        })
        assert response.status_code == 204
        assert current_user.is_authenticated

def test_login_invalid(client, user: User):
    with client:
        response = client.post('/api/login', json={
            'nothing': 123,
            'nothing2': 456,
        })
        assert response.status_code == 400
        assert not current_user.is_authenticated

def test_login_fail(client, user: User):
    with client:
        response = client.post('/api/login', json={
            'username': 'Unknown user',
            'password': 'wrongpassword',
            'remember_login': False,
        })
        assert response.status_code == 401
        assert not current_user.is_authenticated

def test_login_already_logged_in(logged_in_no_permissions_client):
    with logged_in_no_permissions_client:
        response = logged_in_no_permissions_client.post('/api/login', json={
            'username': 'wronguser',
            'password': 'wrongpassword',
            'remember_login': False,
        })
        assert response.status_code == 204


def test_logout(app, logged_in_no_permissions_client):
    with logged_in_no_permissions_client, app.app_context():
       logged_in_no_permissions_client.get('/api/logout')
       assert not current_user.is_authenticated


# password

def test_create_permanent_password_persistence(
    app, logged_in_temporary_password_client
):
    with logged_in_temporary_password_client:
        response = logged_in_temporary_password_client.post(
            '/api/me/permanent-password', json={
                'password': 'new_password'
            }
        )
        assert response.status_code == 204
        with app.app_context():
            assert not current_user.is_password_temporary
            assert current_user.check_password('new_password')

def test_create_permanent_password_invalid(
    logged_in_temporary_password_client
):
    with logged_in_temporary_password_client:
        response = logged_in_temporary_password_client.post(
            '/api/me/permanent-password', json={
                'wrong': 123
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_create_permanent_password_invalid_too_short_password(
    logged_in_temporary_password_client
):
    with logged_in_temporary_password_client:
        response = logged_in_temporary_password_client.post(
            '/api/me/permanent-password', json={
                'password': 'a' * (User.MIN_PASSWORD_LENGTH-1)
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_password_length'

def test_create_permanent_password_invalid_too_long_password(
    logged_in_temporary_password_client
):
    with logged_in_temporary_password_client:
        response = logged_in_temporary_password_client.post(
            '/api/me/permanent-password', json={
                'password': 'a' * (User.MAX_PASSWORD_LENGTH+1)
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_password_length'

def test_create_permanent_password_rejects_user_with_password_already_permanent(
    app, logged_in_no_permissions_client
):
    with logged_in_no_permissions_client:
        response = logged_in_no_permissions_client.post(
            '/api/me/permanent-password', json={
                'password': 'new_password'
            }
        )
        assert response.status_code == 409
        assert response.json['error'] == 'password_already_permanent'

def test_create_permanent_password_rejects_same_as_temporary_password(
    app, logged_in_temporary_password_client
):
    with logged_in_temporary_password_client:
        response = logged_in_temporary_password_client.post(
            '/api/me/permanent-password', json={
                'password': 'password1'
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'same_as_temporary'


def test_change_password_persistence(
    app, logged_in_no_permissions_client
):
    with logged_in_no_permissions_client:
        response = logged_in_no_permissions_client.put(
            '/api/me/password', json={
                'current_password': 'password1',
                'password': 'new_password'
            }
        )
        assert response.status_code == 204
        with app.app_context():
            assert current_user.check_password('new_password')

def test_change_password_invalid(
    logged_in_no_permissions_client
):
    with logged_in_no_permissions_client:
        response = logged_in_no_permissions_client.put(
            '/api/me/password', json={
                'wrong': 123
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_change_password_invalid_too_short_password(
    logged_in_no_permissions_client
):
    with logged_in_no_permissions_client:
        response = logged_in_no_permissions_client.put(
            '/api/me/password', json={
                'current_password': 'password1',
                'password': 'a' * (User.MIN_PASSWORD_LENGTH-1)
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_password_length'

def test_change_password_invalid_too_long_password(
    logged_in_no_permissions_client
):
    with logged_in_no_permissions_client:
        response = logged_in_no_permissions_client.put(
            '/api/me/password', json={
                'current_password': 'password1',
                'password': 'a' * (User.MAX_PASSWORD_LENGTH+1)
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_password_length'

def test_change_password_incorrect_current_password(
    app, logged_in_no_permissions_client
):
    with logged_in_no_permissions_client:
        response = logged_in_no_permissions_client.put(
            '/api/me/password', json={
                'current_password': 'wrong_password',
                'password': 'new_password'
            }
        )
        assert response.status_code == 401
        assert response.json['error'] == 'incorrect_current_password'


# TODO: test last_password_change_time


# preferences

def test_get_own_preferences(app, logged_in_no_permissions_client):
    with logged_in_no_permissions_client, app.app_context():
        response = logged_in_no_permissions_client.get('/api/me/preferences')
        assert response.json['display_name'] == current_user.display_name
        assert response.json['username'] == current_user.username
        assert response.json['homepage'] == current_user.homepage
        assert response.json['temperature_unit'] == current_user.temperature_unit


def test_change_own_preferences_persistence_for_non_admin_user(
    app, logged_in_no_permissions_client
):
    new_preferences = {
        'display_name': 'User',  # ignored for non-admin users
        'username': 'new_username',
        'homepage': User.WebPage.VERIFY_REPORTS.value,
        'temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
    }
    with logged_in_no_permissions_client, app.app_context():
        response = logged_in_no_permissions_client.put(
            '/api/me/preferences',
            json=new_preferences
        )
        assert response.status_code == 204
        for key in new_preferences:
            assert getattr(current_user, key) == new_preferences[key]

def test_change_own_preferences_ignores_display_name_for_non_admin_user(
    app, logged_in_no_permissions_client
):
    new_preferences = {
        'display_name': 'New but ignored display name',
        'username': 'new_username',
        'homepage': User.WebPage.VERIFY_REPORTS.value,
        'temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
    }
    with logged_in_no_permissions_client, app.app_context():
        response = logged_in_no_permissions_client.put(
            '/api/me/preferences',
            json=new_preferences
        )
        assert response.status_code == 204
        assert current_user.display_name == 'User'

def test_change_own_preferences_persistence_for_admin(
    app, logged_in_admin_client
):
    new_preferences = {
        'display_name': 'Updated display name',
        'username': 'new_username',
        'homepage': User.WebPage.VERIFY_REPORTS.value,
        'temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
    }
    with logged_in_admin_client, app.app_context():
        response = logged_in_admin_client.put(
            '/api/me/preferences',
            json=new_preferences
        )
        assert response.status_code == 204
        for key in new_preferences:
            assert getattr(current_user, key) == new_preferences[key]

def test_change_own_preferences_invalid(app, logged_in_no_permissions_client):
    with logged_in_no_permissions_client:
        response = logged_in_no_permissions_client.put(
            '/api/me/preferences',
            json={ 'wrong': 123 }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_change_own_preferences_invalid_too_short_display_name_for_admin(
    app, logged_in_admin_client
):
    with logged_in_admin_client, app.app_context():
        response = logged_in_admin_client.put(
            '/api/me/preferences',
            json={
                'display_name': 'a' * (User.MIN_NAME_LENGTH-1),
                'username': 'new_username',
                'homepage': User.WebPage.VERIFY_REPORTS.value,
                'temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_display_name'

def test_change_own_preferences_invalid_too_long_display_name_for_admin(
    app, logged_in_admin_client
):
    with logged_in_admin_client, app.app_context():
        response = logged_in_admin_client.put(
            '/api/me/preferences',
            json={
                'display_name': 'a' * (User.MAX_NAME_LENGTH+1),
                'username': 'new_username',
                'homepage': User.WebPage.VERIFY_REPORTS.value,
                'temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_display_name'

def test_change_own_preferences_rejects_username_with_spaces(
    app, logged_in_no_permissions_client
):
    with logged_in_no_permissions_client, app.app_context():
        response = logged_in_no_permissions_client.put(
            '/api/me/preferences',
            json={
                'display_name': 'User',
                'username': 'username with spaces',
                'homepage': User.WebPage.VERIFY_REPORTS.value,
                'temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_username'

def test_change_own_preferences_invalid_too_short_username(
    app, logged_in_no_permissions_client
):
    with logged_in_no_permissions_client, app.app_context():
        response = logged_in_no_permissions_client.put(
            '/api/me/preferences',
            json={
                'display_name': 'User',
                'username': 'a' * (User.MIN_NAME_LENGTH-1),
                'homepage': User.WebPage.VERIFY_REPORTS.value,
                'temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_username'

def test_change_own_preferences_invalid_too_long_username(
    app, logged_in_no_permissions_client
):
    with logged_in_no_permissions_client, app.app_context():
        response = logged_in_no_permissions_client.put(
            '/api/me/preferences',
            json={
                'display_name': 'User',
                'username': 'a' * (User.MAX_NAME_LENGTH+1),
                'homepage': User.WebPage.VERIFY_REPORTS.value,
                'temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_username'

def test_change_own_preferences_invalid_homepage(
    app, logged_in_admin_client
):
    with logged_in_admin_client, app.app_context():
        response = logged_in_admin_client.put(
            '/api/me/preferences',
            json={
                'display_name': 'User',
                'username': 'new_username',
                'homepage': 'invalid',
                'temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_change_own_preferences_invalid_temperature_unit(
    app, logged_in_admin_client
):
    with logged_in_admin_client, app.app_context():
        response = logged_in_admin_client.put(
            '/api/me/preferences',
            json={
                'display_name': 'User',
                'username': 'new_username',
                'homepage': User.WebPage.VERIFY_REPORTS.value,
                'temperature_unit': 'invalid',
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_change_own_preferences_rejects_duplicated_username(
    app, logged_in_no_permissions_client, user
):
    with logged_in_no_permissions_client, app.app_context():
        response = logged_in_no_permissions_client.put(
            '/api/me/preferences',
            json={
                'display_name': 'User',
                'username': user.username,
                'homepage': User.WebPage.VERIFY_REPORTS.value,
                'temperature_unit': User.TemperatureUnit.FAHRENHEIT.value,
            }
        )
        assert response.status_code == 400
        assert response.json['error'] == 'username_already_exists'


# TODO: test api_own_preferences_timestamp
