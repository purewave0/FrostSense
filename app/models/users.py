from datetime import datetime
from enum import Enum

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.util import utcnow


class User(UserMixin, db.Model):
    __tablename__ = 'User'

    class WebPage(Enum):
        """Webpage that can be set as a homepage by the user."""
        READINGS       = 'readings'
        HISTORY        = 'history'
        SENSORS        = 'sensors'
        REPORTS        = 'reports'
        VERIFY_REPORTS = 'verify_reports'

    class TemperatureUnit(Enum):
        """Unit used to display temperatures in gauges, graphs, reports, etc."""
        CELSIUS    = 'celsius'
        FAHRENHEIT = 'fahrenheit'

    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 32
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 100

    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: display_name and username
    name: Mapped[str] = mapped_column(
        db.String(MAX_NAME_LENGTH), unique=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(db.String(256))
    created_on: Mapped[datetime] = mapped_column(server_default=utcnow())

    def __init__(self, name: str, password: str):
        self.name = name
        self.password_hash = generate_password_hash(
            password
        )

    def __repr__(self):
        return f'<User "{self.name}">'

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)
