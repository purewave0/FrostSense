from collections.abc import Callable
from functools import wraps

from flask import abort, request, jsonify, redirect, url_for
from flask_login import current_user, login_required

from app.models.users import User


def permission_required(permission: User.Permission):
    """Return an HTTP 403 error if the current user doesn't have `permission`."""
    def decorator(function: Callable):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                return abort(403)
            return function(*args, **kwargs)
        return decorated_function
    return decorator


def login_and_permanent_password_required(view):
    """Run the `LoginManager.unauthorized_handler` if the user is not logged in; else,
    return an HTTP 403 error if the user hasn't created a permanent password yet.
    """
    @wraps(view)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_password_temporary:
            return view(*args, **kwargs)

        if request.blueprint == 'api':
            return jsonify({'error': 'must_create_password'}), 403

        return redirect(url_for('main.create_own_password'))
    return decorated_function
