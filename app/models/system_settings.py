from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


defaultSystemSettings = {
    'default_temperature_unit': 'celsius',
    'minimum_gauge_value': -20,
    'maximum_gauge_value':  40,
    'minimum_graph_value': -20,
    'maximum_graph_value':  40,
}


class SystemSetting(db.Model):
    __tablename__ = 'SystemSetting'

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(
        db.String(32), unique=True, index=True
    )
    value: Mapped[str] = mapped_column(
        db.String(32)
    )
