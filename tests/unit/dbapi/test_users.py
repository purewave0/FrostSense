from collections.abc import Sequence
from datetime import datetime

from app.extensions import db
from app.dbapi import (
    get_users,
    get_user_by_id,
    get_user_by_username,
    get_admin,
    get_user_ids,
    user_id_exists,
    create_user,
    update_user_by_id,
    update_user_permissions_by_id,
    update_user_password_by_id,
    get_user_last_password_change_time_by_id,
    delete_user_by_id,
    get_user_last_update_time,
)
from app.models.users import User


# get

def test_get_users_order_and_result(app, users: Sequence[User]):
    with app.app_context():
        returned_users = get_users()

        assert len(returned_users) == len(users)
        for returned_user, expected_user in zip(returned_users, users):
            assert returned_user['id'] == expected_user.id
            assert returned_user['display_name'] == expected_user.display_name
            assert returned_user['username'] == expected_user.username

def test_get_user_by_id_found_and_not_found(app, user: User):
    with app.app_context():
        returned_user = get_user_by_id(user.id)

        assert returned_user is not None
        assert returned_user == user

        assert get_user_by_id(12345) is None

def test_get_user_by_username_found_and_not_found(app, user: User):
    with app.app_context():
        returned_user = get_user_by_username(user.username)

        assert returned_user is not None
        assert returned_user == user

        assert get_user_by_username('Unknown sensor') is None

def test_get_admin_result(app, admin):
    with app.app_context():
        returned_admin = get_admin()

        assert returned_admin is not None
        assert returned_admin == admin


# get attributes

def test_get_user_ids_order_and_result(app, users: Sequence[User]):
    with app.app_context():
        returned_user_ids = get_user_ids()
        assert len(returned_user_ids) == len(users)

        expected_user_ids = (user.id for user in users)

        for returned_user_id, expected_user_id in zip(
            returned_user_ids, expected_user_ids
        ):
            assert returned_user_id == expected_user_id

def test_get_user_last_password_change_time_by_id_result(app, user: User):
    with app.app_context():
        timestamp = datetime(2025, 8, 1, 12, 34, 56)
        user.password_changed_on = timestamp
        returned_timestamp = get_user_last_password_change_time_by_id(user.id)
        assert returned_timestamp == timestamp

def test_get_user_last_update_time_result(app, user: User):
    with app.app_context():
        timestamp = datetime(2025, 8, 1, 12, 34, 56)
        user.updated_on = timestamp
        returned_timestamp = get_user_last_update_time(user.id)
        assert returned_timestamp == timestamp


# exists

def test_user_id_exists_found_and_not_found(app, user: User):
    with app.app_context():
        assert user_id_exists(user.id)
        assert not user_id_exists(1234)


# create

def test_create_user_result_and_persistence_and_password(app):
    with app.app_context():
        user = create_user(
            'Test user 1',
            'testuser1',
            'password1',
            False,
            User.Permission(0),
            User.WebPage.READINGS,
            User.TemperatureUnit.CELSIUS,
        )

        stored_user = db.session.execute(
            db.select(
                User
            ).where(
                User.id == user.id
            )
        ).scalar_one_or_none()
        assert stored_user is not None
        assert stored_user == user
        assert stored_user.check_password('password1')


# update

def test_update_user_by_id_persistence_and_timestamp(app, user: User):
    with app.app_context():
        old_update_timestamp = user.updated_on

        update_user_by_id(
            user.id,
            'Updated user 1',
            'updateduser1',
            User.Permission.ASSIGNABLE_PERMISSIONS,
            User.WebPage.HISTORY,
            User.TemperatureUnit.FAHRENHEIT
        )

        stored_user = db.session.execute(
            db.select(
                User
            ).where(
                User.id == user.id
            )
        ).scalar_one()
        assert stored_user.display_name == 'Updated user 1'
        assert stored_user.username == 'updateduser1'
        assert stored_user.permissions == User.Permission.ASSIGNABLE_PERMISSIONS.value
        assert stored_user.homepage == User.WebPage.HISTORY
        assert stored_user.temperature_unit == User.TemperatureUnit.FAHRENHEIT
        assert stored_user.updated_on > old_update_timestamp


def test_update_user_permissions_by_id_persistence_and_timestamp(app, user: User):
    with app.app_context():
        old_update_timestamp = user.updated_on

        update_user_permissions_by_id(user.id, User.Permission.ASSIGNABLE_PERMISSIONS)

        updated_user = db.session.execute(
            db.select(
                User
            ).where(
                User.id == user.id
            )
        ).scalar_one()
        assert updated_user.permissions == User.Permission.ASSIGNABLE_PERMISSIONS.value
        assert updated_user.updated_on > old_update_timestamp

def test_update_user_password_by_id_temporary_and_permanent_persistence_and_timestamps(
    app, user: User
):
    with app.app_context():
        for password, is_temporary in (
            ('temporarypassword1', True), ('permanentpassword1', False)
        ):
            old_user = db.session.execute(
                db.select(
                    User
                ).where(
                    User.id == user.id
                )
            ).scalar_one()
            old_update_timestamp = old_user.updated_on
            old_password_change_timestamp = old_user.password_changed_on

            update_user_password_by_id(user.id, password, is_temporary)

            updated_user = db.session.execute(
                db.select(
                    User
                ).where(
                    User.id == user.id
                )
            ).scalar_one()
            assert updated_user.check_password(password)
            assert updated_user.updated_on > old_update_timestamp
            assert updated_user.is_password_temporary == is_temporary
            is_second_password_change = password == 'permanentpassword1'
            if is_second_password_change:
                # the password was changed before. does the password change timestamp
                # correctly reflect that?
                assert updated_user.password_changed_on > old_password_change_timestamp


# delete

def test_delete_user_by_id_persistence(app, user: User):
    with app.app_context():
        delete_user_by_id(user.id)

        stored_user = db.session.execute(
            db.select(
                User
            ).where(
                User.id == user.id
            )
        ).scalar_one_or_none()
        assert stored_user is None
