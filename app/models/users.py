from datetime import datetime
from enum import Enum, Flag
from random import randint
from colorsys import hls_to_rgb
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
        """The user can edit sensor names."""
        MANAGE_USERS = 4
        """The user can view, create, edit, and delete users."""
        MANAGE_SYSTEM_SETTINGS = 8
        """The user can edit system settings."""
        ADMIN = MANAGE_REPORTS | EDIT_SENSORS | MANAGE_USERS | MANAGE_SYSTEM_SETTINGS
        """Shorthand for all permissions."""
        ASSIGNABLE_PERMISSIONS = MANAGE_REPORTS | EDIT_SENSORS
        """Permissions that can be granted through the web interface."""

        def has_permission(self, other: 'User.Permission') -> bool:
            return (self & other).value == other.value

    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 32
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 100
    _TEMPORARY_PASSWORD_CHARSET = string.ascii_lowercase + string.digits

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(
        db.String(MAX_NAME_LENGTH), index=True
    )
    username: Mapped[str] = mapped_column(
        db.String(MAX_NAME_LENGTH), unique=True, index=True
    )
    avatar_colour: Mapped[str] = mapped_column(db.String(7))
    password_hash: Mapped[str] = mapped_column(db.String(256))
    is_password_temporary: Mapped[bool] = mapped_column()
    password_changed_on: Mapped[datetime | None] = mapped_column()
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
        self.avatar_colour = User._generate_random_avatar_colour()
        self.permissions = permissions.value
        self.homepage = homepage
        self.temperature_unit = temperature_unit
        self.password_hash = generate_password_hash(password)
        self.is_password_temporary = is_password_temporary
        self.password_changed_on = None


    def __repr__(self):
        return f'<User "{self.display_name}" ({self.username})>'

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission_value: Permission) -> bool:
        return User.Permission(self.permissions).has_permission(permission_value)

    @staticmethod
    def _generate_random_avatar_colour() -> str:
        """Return a random, slightly dark colour meant for avatar backgrounds.
        The colour is returned as a HEX string (#abc123).
        """
        def rgb_to_hex(r: int, g: int, b: int) -> int:
            return (r << 16) | (g << 8) | b

        HUE_LIMIT = 1  # 100% in decimal
        LIGHTNESS = 0.35  # slightly dark so we can use white text
        SATURATION = 0.8
        hue = randint(0, HUE_LIMIT*100) / 100
        rgb_colour_floats = hls_to_rgb(hue, LIGHTNESS, SATURATION)
        # hls_to_rgb returns floats between 0 and 1. convert them
        # to 8-bit values (0-255)
        colour_rgb = tuple(
            int(value*255) for value in rgb_colour_floats
        )
        colour_hex = rgb_to_hex(*colour_rgb)
        return f'#{colour_hex:06x}'

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
