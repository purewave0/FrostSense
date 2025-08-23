from datetime import datetime
from enum import Enum

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
        VERIFY_REPORTS = 'verify_reports'

    # subclassing str for easy JSON serialisation
    class TemperatureUnit(str, Enum):
        """Unit used to display temperatures in gauges, graphs, reports, etc."""
        CELSIUS    = 'celsius'
        FAHRENHEIT = 'fahrenheit'

    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 32
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 100

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(
        db.String(MAX_NAME_LENGTH), unique=True, index=True
    )
    username: Mapped[str] = mapped_column(
        db.String(MAX_NAME_LENGTH), unique=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(db.String(256))
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
        username: str, password: str,
        homepage: WebPage = WebPage.READINGS,
        temperature_unit: TemperatureUnit = TemperatureUnit.CELSIUS
    ):
        self.display_name = display_name
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.homepage = homepage
        self.temperature_unit = temperature_unit

    def __repr__(self):
        return f'<User "{self.display_name}" ({self.username})>'

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)
