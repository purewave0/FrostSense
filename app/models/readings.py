from datetime import datetime
import string, secrets

from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.util import utcnow


class Sensor(db.Model):
    __tablename__ = 'Sensor'

    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 64
    _KEY_CHARSET = string.ascii_letters + string.digits
    _KEY_LENGTH = 24

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        db.String(MAX_NAME_LENGTH), unique=True,
    )
    key: Mapped[str] = mapped_column(db.String(_KEY_LENGTH), unique=True)
    created_on: Mapped[datetime] = mapped_column(server_default=utcnow())

    def __init__(self, name):
        self.name = name
        self.key = Sensor._generate_key()

    @staticmethod
    def _generate_key() -> str:
        """Return a 24-character-long key made of lower+uppercase letters and digits."""
        return ''.join(
            secrets.choice(Sensor._KEY_CHARSET)
            for _ in range(Sensor._KEY_LENGTH)
        )


class Reading(db.Model):
    __tablename__ = 'Reading'

    id: Mapped[int] = mapped_column(primary_key=True)
    sensor_id: Mapped[int] = mapped_column(db.ForeignKey('Sensor.id'))
    temperature: Mapped[float] = mapped_column()
    created_on: Mapped[datetime] = mapped_column(server_default=utcnow())

    def __init__(
        self,
        sensor_id: int,
        temperature: float,
        created_on: datetime | None = None
    ):
        self.sensor_id = sensor_id
        self.temperature = temperature
        if created_on is not None:
            self.created_on = created_on

    def __repr__(self):
        return (
            f'<Reading from {self.sensor_id}: {self.temperature} °C on'
            + f' {self.created_on}>'
        )
