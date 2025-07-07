from datetime import datetime

from app.extensions import db
from app.models.util import utcnow


class Sensor(db.Model):
    __tablename__ = 'Sensor'

    MAX_NAME_LENGTH = 64

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(MAX_NAME_LENGTH), nullable=False, unique=True,
    )
    created_on = db.Column(db.DateTime, server_default=utcnow())
    # TODO: secret key tied to the board, so (fake) readings can't just be sent to
    # whatever ID

    def __init__(self, name):
        self.name = name


class Reading(db.Model):
    __tablename__ = 'Reading'

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('Sensor.id'))
    temperature = db.Column(db.Float, nullable=True)
    created_on = db.Column(db.DateTime, server_default=utcnow(), nullable=False)

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
