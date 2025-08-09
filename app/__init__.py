from datetime import datetime, date
from os import makedirs

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_login import LoginManager

from app.extensions import db
from app.api.report import REPORTS_DIRECTORY
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
    login_manager = LoginManager(app)

    with app.app_context():
        from app.models.readings import Sensor, Reading
        from app.models.users import User
        db.create_all()

        @login_manager.user_loader
        def load_user(user_id: int) -> User | None:
            user = db.session.execute(
                    db.select(User).where(User.id == int(user_id))
                ).scalar_one_or_none()
            return user

        login_manager.login_view = 'main.login'  # type: ignore[attr-defined]


    # -- blueprints --
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # -- cli --
    from app.cli import register_commands
    register_commands(app)

    # -- dirs --
    makedirs(REPORTS_DIRECTORY, exist_ok=True)

    return app
