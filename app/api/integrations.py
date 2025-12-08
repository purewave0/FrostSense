from datetime import datetime, timezone

from app.dbapi import get_webhooks
from app.models.integrations import IntegrationProvider

import requests


def send_temperature_alert(
    sensor_id: int,
    sensor_name: str,
    temperature: float,
    threshold_type: str,
    threshold_temperature: float
):
    for webhook in get_webhooks():
        payload = None
        # each provider expects a specific payload
        match webhook.provider:
            case IntegrationProvider.DISCORD:
                status = (
                    '🔺 Over threshold' if threshold_type == 'max'
                    else '🔻 Under threshold'
                )
                payload = {
                    'username': 'FrostSense Alert',
                    # TODO: png logo for the avatar
                    'embeds': [
                        {
                            'title': 'Temperature Alert',
                            'description': f'**Status:** {status}',
                            'fields': [
                                { 'name': 'Sensor Name', 'value': sensor_name, 'inline': True },
                                { 'name': 'Sensor ID', 'value': f'`{sensor_id}`', 'inline': True },
                                # TODO: follow system settings' temperature unit
                                { 'name': 'Temperature', 'value': f'{temperature} °C', 'inline': True },
                                { 'name': 'Threshold', 'value': f'{threshold_temperature} °C', 'inline': True }
                            ],
                            'timestamp': datetime.now(timezone.utc).isoformat(),
                        }
                    ]
                }

        requests.post(webhook.url, json=payload)
