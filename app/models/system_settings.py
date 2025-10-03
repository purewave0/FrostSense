from datetime import datetime
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.util import utcnow


default_system_settings_base: dict[str, dict[str, Any]] = {
    'default_temperature_unit': {
        'value': 'celsius'
    },
    'minimum_gauge_value': {
        'value': -30,
        'min': -50,
        'max': 5,
    },
    'maximum_gauge_value': {
        'value': 40,
        'min': 10,
        'max': 60,
    },
    'minimum_graph_value': {
        'value': -30,
        'min': -50,
        'max': 5,
    },
    'maximum_graph_value': {
        'value': 40,
        'min': 10,
        'max': 60,
    },
}


class SystemSetting(db.Model):
    """A global setting, editable by the admin."""
    __tablename__ = 'SystemSetting'

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(
        db.String(32), unique=True, index=True
    )
    """The setting's name."""
    value: Mapped[str] = mapped_column(
        db.String(32)
    )
    """The setting's value."""


class SystemSettingsTimestamp(db.Model):
    """A timestamp for system settings updates."""
    __tablename__ = 'SystemSettingsTimestamp'

    id: Mapped[int] = mapped_column(primary_key=True)
    updated_on: Mapped[datetime] = mapped_column(
        server_default=utcnow()
    )
    """When the last settings were last updated."""
