from datetime import datetime
from enum import Enum, Flag
import string, secrets

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.util import utcnow


class User(UserMixin, db.Model):
    __tablename__ = 'User'

    # subclassing str for easy JSON serialisation
    class WebPage(str, Enum):
        """Webpage that can be set as a homepage by the user."""
        READINGS       = 'readings'
        HISTORY        = 'history'
        SENSORS        = 'sensors'
        REPORTS        = 'reports'
        VERIFY_REPORTS = 'verify-reports'

    # subclassing str for easy JSON serialisation
    class TemperatureUnit(str, Enum):
        """Unit used to display temperatures in gauges, graphs, reports, etc."""
        CELSIUS    = 'celsius'
        FAHRENHEIT = 'fahrenheit'

    class Permission(Flag):
        """Permission flags for actions and resources."""
        MANAGE_REPORTS = 1
        """The user can view, generate, and verify reports."""
        EDIT_SENSORS = 2
        """The user can edit sensor properties like name and status(TODO)."""
        MANAGE_USERS = 4
        """The user can view, create, edit, and delete users."""
        MANAGE_SYSTEM_SETTINGS = 8
        """The user can edit system settings."""
        ADMIN = MANAGE_REPORTS | EDIT_SENSORS | MANAGE_USERS | MANAGE_SYSTEM_SETTINGS
        """Shorthand for all permissions."""

        def has_permission(self, other: 'User.Permission') -> bool:
            return (self & other).value != 0

    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 32
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 100
    _TEMPORARY_PASSWORD_CHARSET = string.ascii_lowercase + string.digits

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(
        db.String(MAX_NAME_LENGTH), index=True
    )
    username: Mapped[str] = mapped_column(
        db.String(MAX_NAME_LENGTH), unique=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(db.String(256))
    is_password_temporary: Mapped[bool] = mapped_column()
    permissions: Mapped[int] = mapped_column()
    created_on: Mapped[datetime] = mapped_column(server_default=utcnow())
    updated_on: Mapped[datetime] = mapped_column(
        server_default=utcnow(), onupdate=utcnow()
    )
    homepage: Mapped[WebPage] = mapped_column(default=WebPage.READINGS)
    temperature_unit: Mapped[TemperatureUnit] = mapped_column(
        default=TemperatureUnit.CELSIUS
    )

    def __init__(
        self,
        display_name: str,
        username: str,
        password: str,
        is_password_temporary: bool,
        permissions: Permission,
        homepage: WebPage = WebPage.READINGS,
        temperature_unit: TemperatureUnit = TemperatureUnit.CELSIUS
    ):
        self.display_name = display_name
        self.username = username
        self.permissions = permissions.value
        self.homepage = homepage
        self.temperature_unit = temperature_unit
        self.password_hash = generate_password_hash(password)
        self.is_password_temporary = is_password_temporary


    def __repr__(self):
        return f'<User "{self.display_name}" ({self.username})>'

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission_value: Permission) -> bool:
        return User.Permission(self.permissions).has_permission(permission_value)

    @staticmethod
    def generate_password_hash(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def generate_temporary_password() -> str:
        """Return a 12-character-long password made of lowercase letters and digits."""
        return ''.join(
            secrets.choice(User._TEMPORARY_PASSWORD_CHARSET)
            for _ in range(12)
        )
