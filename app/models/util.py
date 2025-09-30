from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles

from app.extensions import db


class utcnow(expression.FunctionElement):
    """The current time in UTC."""
    type = db.DateTime()
    inherit_cache = True

@compiles(utcnow, 'mariadb')
def pg_utcnow(element, compiler, **kw):
    """Return the current time in UTC."""
    return "UTC_TIMESTAMP"
