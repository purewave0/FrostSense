from app.models.integrations import IntegrationProvider, TemperatureAlert, Webhook
from app.models.readings import Sensor
from app.dbapi import (
    create_webhook, delete_webhook_by_id, get_webhooks,
    create_temperature_alert, delete_temperature_alert_by_id,
    get_temperature_alerts,
)
from app.extensions import db


# -- webhooks --

# create

def test_create_webhook_result_and_persistence(app):
    with app.app_context():
        webhook = create_webhook(IntegrationProvider.DISCORD, 'https://example.com')

        stored_webhook = db.session.execute(
            db.select(
                Webhook
            ).where(
                Webhook.id == webhook['id']
            )
        ).scalar_one()
        assert stored_webhook.provider is IntegrationProvider.DISCORD
        assert stored_webhook.url == 'https://example.com'


# delete

def test_delete_webhook_persistence(app, webhook: Webhook):
    with app.app_context():
        delete_webhook_by_id(webhook.id)

        stored_webhook = db.session.execute(
            db.select(
                Webhook
            ).where(
                Webhook.id == webhook.id
            )
        ).scalar_one_or_none()
        assert stored_webhook is None


# get

def test_get_webhooks_order_and_result(
    app, webhooks: tuple[Webhook, ...]
):
    with app.app_context():
        returned_webhooks = get_webhooks()
        assert len(returned_webhooks) == len(webhooks)

        for returned_webhook, webhook in zip(returned_webhooks, webhooks):
            assert returned_webhook.id == webhook.id
            assert returned_webhook.provider is webhook.provider
            assert returned_webhook.url == webhook.url


# -- temperature alerts --

# create

def test_create_temperature_alert_result_and_persistence(app):
    with app.app_context():
        alert = create_temperature_alert(
            -40.5,
            40.5
        )
        assert alert['is_active']
        assert alert['min_threshold'] == -40.5
        assert alert['max_threshold'] == 40.5
        assert alert['created_on'] is not None

        stored_alert = db.session.execute(
            db.select(
                TemperatureAlert
            ).where(
                TemperatureAlert.id == alert['id']
            )
        ).scalar_one()
        assert stored_alert.is_active
        assert stored_alert.min_threshold == -40.5
        assert stored_alert.max_threshold == 40.5


# delete

def test_delete_temperature_alert_persistence(app, temperature_alert: TemperatureAlert):
    with app.app_context():
        delete_temperature_alert_by_id(temperature_alert.id)

        stored_alert = db.session.execute(
            db.select(
                TemperatureAlert
            ).where(
                TemperatureAlert.id == temperature_alert.id
            )
        ).scalar_one_or_none()
        assert stored_alert is None


# get

def test_get_temperature_alerts_order_and_result(
    app, temperature_alerts: tuple[TemperatureAlert, ...]
):
    with app.app_context():
        returned_alerts = get_temperature_alerts()
        assert len(returned_alerts) == len(temperature_alerts)

        for returned_alert, alert in zip(returned_alerts, temperature_alerts):
            assert returned_alert['is_active'] == alert.is_active
            assert returned_alert['min_threshold'] == alert.min_threshold
            assert returned_alert['max_threshold'] == alert.max_threshold
            assert returned_alert['created_on'] == alert.created_on
