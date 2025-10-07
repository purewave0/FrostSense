from collections.abc import Sequence
from typing import Any

from flask_login import current_user

from app.extensions import db
from app.models.users import User
from tests.util import parsed_datetime, temporary_password_pattern, avatar_hex_colour_pattern


def test_get_users_order_and_result(app, logged_in_admin_client, users):
    with logged_in_admin_client:
        response = logged_in_admin_client.get('/api/users')
        returned_users: tuple[dict[str, Any], ...] = response.json

        with app.app_context():
            stored_users: Sequence[User] = db.session.execute(
                db.select(
                    User
                ).order_by(
                    User.created_on.asc()
                )
            ).scalars().all()
        assert len(returned_users) == len(stored_users)

        for returned_user, expected_user in zip(returned_users, stored_users):
            assert returned_user['id'] == expected_user.id
            assert returned_user['display_name'] == expected_user.display_name
            assert returned_user['username'] == expected_user.username
            assert avatar_hex_colour_pattern.match(returned_user['avatar_colour'])
            assert returned_user['avatar_colour'] == expected_user.avatar_colour
            assert returned_user['permissions'] == expected_user.permissions
            assert parsed_datetime(returned_user['created_on']) == expected_user.created_on
            assert parsed_datetime(returned_user['updated_on']) == expected_user.updated_on


def test_create_user_result_and_persistence(app, logged_in_admin_client, default_system_settings):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users', json={
            'display_name': 'Test user 1',
            'username': 'testuser1',
            'permissions': 0,
        })
        assert response.status_code == 201
        created_user = response.json

        with app.app_context():
            stored_user = db.session.execute(
                db.select(
                    User
                ).where(
                    User.id == created_user['id']
                )
            ).scalar_one_or_none()
        assert stored_user is not None
        assert created_user['display_name'] == stored_user.display_name == 'Test user 1'
        assert created_user['username'] == stored_user.username == 'testuser1'
        assert avatar_hex_colour_pattern.match(stored_user.avatar_colour)
        assert stored_user.is_password_temporary
        assert temporary_password_pattern.match(created_user['temporary_password'])
        assert created_user['permissions'] == stored_user.permissions == 0
        assert parsed_datetime(created_user['created_on']) == stored_user.created_on
        assert parsed_datetime(created_user['updated_on']) == stored_user.updated_on

def test_create_user_invalid(app, logged_in_admin_client):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users', json={
            'wrong': 123
        })
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_create_user_invalid_too_short_display_name(app, logged_in_admin_client):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users', json={
            'display_name': 'a' * (User.MIN_NAME_LENGTH-1),
            'username': 'testuser1',
            'permissions': 0,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_display_name'

def test_create_user_invalid_too_long_display_name(app, logged_in_admin_client):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users', json={
            'display_name': 'a' * (User.MAX_NAME_LENGTH+1),
            'username': 'testuser1',
            'permissions': 0,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_display_name'

def test_create_user_invalid_too_short_username(app, logged_in_admin_client):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users', json={
            'display_name': 'Test user 1',
            'username': 'a' * (User.MIN_NAME_LENGTH-1),
            'permissions': 0,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_username'

def test_create_user_invalid_too_long_username(app, logged_in_admin_client):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users', json={
            'display_name': 'Test user 1',
            'username': 'a' * (User.MAX_NAME_LENGTH+1),
            'permissions': 0,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_username'

def test_create_user_invalid_permission(app, logged_in_admin_client):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users', json={
            'display_name': 'Test user 1',
            'username': 'testuser1',
            'permissions': 12345,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_create_user_invalid_negative_permission(app, logged_in_admin_client):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users', json={
            'display_name': 'Test user 1',
            'username': 'testuser1',
            'permissions': -1,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_create_user_illegal_permission(app, logged_in_admin_client):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users', json={
            'display_name': 'Test user 1',
            'username': 'testuser1',
            'permissions': User.Permission.MANAGE_USERS.value,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'illegal_permission'

def test_create_user_rejects_duplicate_username(app, logged_in_admin_client, user):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users', json={
            'display_name': 'Test user 1',
            'username': user.username,
            'permissions': 0,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'username_already_exists'


# TODO: test users summary


def test_delete_user_persistence(app, logged_in_admin_client, user):
    with logged_in_admin_client:
        response = logged_in_admin_client.delete(f'/api/users/{user.id}')
        assert response.status_code == 204
        with app.app_context():
            deleted_user = db.session.execute(
                db.select(
                    User
                ).where(
                    User.id == user.id
                )
            ).scalar_one_or_none()
        assert deleted_user is None


def test_update_user_persistence(app, logged_in_admin_client, user, default_system_settings):
    with logged_in_admin_client:
        response = logged_in_admin_client.put(f'/api/users/{user.id}', json={
            'display_name': 'Updated user 1',
            'permissions': (
                User.Permission.EDIT_SENSORS | User.Permission.MANAGE_REPORTS
            ).value,
        })
        assert response.status_code == 204

        with app.app_context():
            updated_user: User = db.session.execute(
                db.select(
                    User
                ).where(
                    User.id == user.id
                )
            ).scalar_one()
        assert updated_user.display_name == 'Updated user 1'
        assert updated_user.permissions == (
            User.Permission.EDIT_SENSORS | User.Permission.MANAGE_REPORTS
        ).value
        assert updated_user.updated_on > updated_user.created_on

def test_update_user_invalid(app, logged_in_admin_client, user):
    with logged_in_admin_client:
        response = logged_in_admin_client.put(f'/api/users/{user.id}', json={
            'wrong': 123
        })
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_update_user_unknown_user(app, logged_in_admin_client, user):
    with logged_in_admin_client:
        response = logged_in_admin_client.put('/api/users/123', json={
            'display_name': 'Updated user 1',
            'permissions': (
                User.Permission.EDIT_SENSORS | User.Permission.MANAGE_REPORTS
            ).value,
        })
        assert response.status_code == 404
        assert response.json['error'] == 'user_not_found'

def test_update_user_invalid_too_short_display_name(app, logged_in_admin_client, user):
    with logged_in_admin_client:
        response = logged_in_admin_client.put(f'/api/users/{user.id}', json={
            'display_name': 'a' * (User.MIN_NAME_LENGTH-1),
            'permissions': 0,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_display_name'

def test_update_user_invalid_too_long_display_name(app, logged_in_admin_client, user):
    with logged_in_admin_client:
        response = logged_in_admin_client.put(f'/api/users/{user.id}', json={
            'display_name': 'a' * (User.MAX_NAME_LENGTH+1),
            'permissions': 0,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'invalid_display_name'

def test_update_user_invalid_permission(app, logged_in_admin_client, user):
    with logged_in_admin_client:
        response = logged_in_admin_client.put(f'/api/users/{user.id}', json={
            'display_name': 'Updated user 1',
            'permissions': 12345,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_update_user_invalid_negative_permission(app, logged_in_admin_client, user):
    with logged_in_admin_client:
        response = logged_in_admin_client.put(f'/api/users/{user.id}', json={
            'display_name': 'Updated user 1',
            'permissions': -1,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'field_error'

def test_update_user_illegal_permission(app, logged_in_admin_client, user):
    with logged_in_admin_client:
        response = logged_in_admin_client.put(f'/api/users/{user.id}', json={
            'display_name': 'Updated user 1',
            'permissions': User.Permission.MANAGE_USERS.value,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'illegal_permission'

def test_update_user_rejects_self_edit(app, logged_in_admin_client):
    with logged_in_admin_client, app.app_context():
        logged_in_admin_client.get('/')  # to load current_user
        response = logged_in_admin_client.put(f'/api/users/{current_user.id}', json={
            'display_name': 'Updated admin 1',
            'permissions': 0,
        })
        assert response.status_code == 400
        assert response.json['error'] == 'editing_yourself'


def test_reset_user_password_result_and_persistence(logged_in_admin_client, user):
    with logged_in_admin_client:
        response = logged_in_admin_client.post(f'/api/users/{user.id}/reset-password')
        assert response.status_code == 200
        returned_temporary_password = response.json
        assert temporary_password_pattern.match(returned_temporary_password)
        assert user.check_password(returned_temporary_password)

def test_reset_user_password_unknown_user(logged_in_admin_client):
    with logged_in_admin_client:
        response = logged_in_admin_client.post('/api/users/12345/reset-password')
        assert response.status_code == 404
        assert response.json['error'] == 'user_not_found'

def test_reset_user_password_rejects_self_edit(app, logged_in_admin_client):
    with logged_in_admin_client, app.app_context():
        logged_in_admin_client.get('/')  # to load current_user
        response = logged_in_admin_client.post(f'/api/users/{current_user.id}/reset-password')
        assert response.status_code == 400
        assert response.json['error'] == 'editing_yourself'
