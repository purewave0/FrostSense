"""External integrations for sending automated alerts."""

from datetime import datetime
from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.util import utcnow


class IntegrationProvider(str, Enum):
    """The service that will receive the alert."""
    DISCORD = 'discord'


class Webhook(db.Model):
    """Registered webhooks used by all alerts."""
    __tablename__ = 'Webhook'

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[IntegrationProvider] = mapped_column()
    """Where the alert will be sent."""
    url: Mapped[str] = mapped_column(db.String(160), unique=True)
    """The webhook URL."""

    def __init__(
        self,
        provider: IntegrationProvider,
        url: str,
    ):
        self.provider = provider
        self.url = url


class TemperatureAlert(db.Model):
    """External alerts for all sensors based on temperature thresholds."""
    __tablename__ = 'TemperatureAlert'

    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column()
    """Whether the alert is active."""
    min_threshold: Mapped[float | None] = mapped_column()
    """Lower temperature threshold that triggers the alert."""
    max_threshold: Mapped[float | None] = mapped_column()
    """Upper temperature threshold that triggers the alert."""
    created_on: Mapped[datetime] = mapped_column(server_default=utcnow())
    """When the alert was created."""

    def __init__(
        self,
        min_threshold: float | None,
        max_threshold: float | None
    ):
        self.is_active = True

        if min_threshold is None and max_threshold is None:
            raise ValueError('you must specify at least one threshold')

        elif (
            min_threshold is not None and max_threshold is not None
            and not (max_threshold > min_threshold)
        ):
            raise ValueError('max_threshold must be greater than min_threshold')

        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
