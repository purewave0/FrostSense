"""Useful CLI commands for populating the database."""

import click
from flask import current_app

from app.dbapi import create_sensor


def register_commands(app):
    @app.cli.command('seed-sensors')
    @click.option(
        "--count",
        type=int,
        default=4,
        show_default=True,
        help="How many sensors to insert"
    )
    def seed_sensors(count):
        """Seed the database with `count` example sensors."""

        for number in range(1, count+1):
            create_sensor(f'Sensor {number}')

        click.echo(f'seeded {count} sensors.')
