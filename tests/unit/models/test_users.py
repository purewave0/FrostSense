import re

from app.extensions import db
from app.models.users import User
from tests.util import temporary_password_pattern, avatar_hex_colour_pattern


def test_model(app):
    with app.app_context():
        user = User(
            'Test user 1',
            'testuser1',
            'password1',
            False,
            User.Permission(0),
            User.WebPage.READINGS,
            User.TemperatureUnit.CELSIUS,
        )
        db.session.add(user)
        db.session.commit()

        stored_user: User | None = db.session.execute(
            db.select(
                User
            ).where(
                User.id == user.id
            )
        ).scalar_one_or_none()
        assert stored_user is not None
        assert stored_user == user
        assert avatar_hex_colour_pattern.match(user.avatar_colour)
        # check if hashed
        assert stored_user.password_hash != 'password1'

def test_check_password_correct_and_incorrect(app, user):
    assert user.check_password('password1')
    assert not user.check_password('PASSWORD1')
    assert not user.check_password('wrongpassword1')

def test_Permission_enum_has_permission_result(app):
    P = User.Permission
    assert not P(0).has_permission(P.MANAGE_REPORTS)
    assert not P(0).has_permission(P.ADMIN)

    assert P.MANAGE_REPORTS.has_permission(P.MANAGE_REPORTS)
    assert not P.MANAGE_REPORTS.has_permission(P.EDIT_SENSORS)

    two_permissions = P.MANAGE_REPORTS | P.EDIT_SENSORS
    assert two_permissions.has_permission(P.MANAGE_REPORTS)
    assert two_permissions.has_permission(P.EDIT_SENSORS)
    assert not two_permissions.has_permission(P.EDIT_SENSORS | P.MANAGE_USERS)

    assert P.ADMIN.has_permission(two_permissions)

def test_user_has_permission_result(app, user: User):
    P = User.Permission
    assert not user.has_permission(P.MANAGE_REPORTS)
    assert not user.has_permission(P.ADMIN)

    user.permissions = P.MANAGE_REPORTS.value
    assert user.has_permission(P.MANAGE_REPORTS)
    assert not user.has_permission(P.EDIT_SENSORS)

    two_permissions = P.MANAGE_REPORTS | P.EDIT_SENSORS
    user.permissions = two_permissions.value
    assert user.has_permission(P.MANAGE_REPORTS)
    assert user.has_permission(P.EDIT_SENSORS)
    assert not user.has_permission(P.EDIT_SENSORS | P.MANAGE_USERS)

    user.permissions = P.ADMIN.value
    assert user.has_permission(two_permissions)

def test_generate_random_avatar_colour_format(app, user: User):
    assert avatar_hex_colour_pattern.match(
        User._generate_random_avatar_colour()
    )

def test_generate_password_hash_difference(app, user: User):
    assert User.generate_password_hash('password1') != 'password1'

def test_generate_temporary_password_format(app, user: User):
    assert temporary_password_pattern.match(
        User.generate_temporary_password()
    )
