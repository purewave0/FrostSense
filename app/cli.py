"""Useful CLI commands for populating the database."""

import datetime as dt
from random import randrange

import click

from app.dbapi import create_sensor, get_sensors, create_readings


def register_commands(app):
    @app.cli.command('seed-sensors')
    @click.option(
        '--count',
        type=int,
        default=4,
        show_default=True,
        help='How many sensors to insert'
    )
    def seed_sensors(count):
        """Seed the database with `count` example sensors."""

        for number in range(1, count+1):
            create_sensor(f'Sensor {number}')

        click.echo(f'seeded {count} sensors.')


    @app.cli.command('seed-readings')
    @click.option(
        '--count',
        type=int,
        default=120,
        show_default=True,
        help='How many readings per sensor to insert'
    )
    @click.option(
        '--interval',
        type=int,
        default=60,
        show_default=True,
        help='Seconds of interval between the readings'
    )
    def seed_readings(count, interval):
        """Seed the database sensors with `count` random readings.

        Starting from `interval` * `count` seconds before now, readings will have
        `interval` seconds between each other.
        """
        all_sensors = get_sensors()
        start_time = dt.datetime.utcnow() - dt.timedelta(seconds=interval*count)

        for sensor in all_sensors:
            readings = []
            for times in range(count):
                readings.append(
                    {
                        'sensor_id': sensor['id'],
                        'temperature': randrange(-25000, 25000)/1000,
                        'created_on': start_time + dt.timedelta(seconds=interval*times),
                    }
                )

            create_readings(sensor['id'], readings)

        click.echo(
            f'seeded {count} readings x {len(all_sensors)} sensors'
        )
        total_seeded = len(all_sensors) * count
        click.echo(
            f'total: {total_seeded} readings.'
        )
