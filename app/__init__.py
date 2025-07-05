from datetime import datetime, date

from flask import Flask
from flask.json.provider import DefaultJSONProvider

from app.extensions import db
from config import Config


# serialize date(time)s to ISO strings
class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, (date, datetime)):
            return o.isoformat() + 'Z'  # Z = UTC timezone
        return super().default(o)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.json = UpdatedJSONProvider(app)
    app.config.from_object(config_class)

    # -- extensions --
    db.init_app(app)

    with app.app_context():
        from app.models.readings import Sensor, Reading
        db.create_all()

    # -- blueprints --
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
