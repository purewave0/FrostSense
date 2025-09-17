from collections.abc import Callable
from functools import wraps

from flask import abort
from flask_login import current_user

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
