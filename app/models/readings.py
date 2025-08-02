from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.util import utcnow


class Sensor(db.Model):
    __tablename__ = 'Sensor'

    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 64

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        db.String(MAX_NAME_LENGTH), unique=True,
    )
    created_on: Mapped[datetime] = mapped_column(server_default=utcnow())
    # TODO: secret key tied to the board, so (fake) readings can't just be sent to
    # whatever ID

    def __init__(self, name):
        self.name = name


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
