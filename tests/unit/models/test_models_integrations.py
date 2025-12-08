from app.models.integrations import TemperatureAlert, Webhook, IntegrationProvider
from app.extensions import db


# webhooks

def test_webhook_model(app):
    with app.app_context():
        webhook = Webhook(IntegrationProvider.DISCORD, 'https://example.com')
        db.session.add(webhook)
        db.session.commit()

        stored_webhook: Webhook | None = db.session.execute(
            db.select(
                Webhook
            ).where(
                Webhook.id == webhook.id
            )
        ).scalar_one_or_none()
        assert stored_webhook is not None
        assert stored_webhook.provider is IntegrationProvider.DISCORD
        assert stored_webhook.url == 'https://example.com'


# readings

def test_temperature_alert_model(app):
    with app.app_context():
        alert = TemperatureAlert(-30, 30)
        db.session.add(alert)
        db.session.commit()

        stored_alert: TemperatureAlert | None = db.session.execute(
            db.select(
                TemperatureAlert
            ).where(
                TemperatureAlert.id == alert.id
            )
        ).scalar_one_or_none()
        assert stored_alert is not None
        assert stored_alert.min_threshold == -30
        assert stored_alert.max_threshold == 30
