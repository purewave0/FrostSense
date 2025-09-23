"""Useful CLI commands for populating the database."""

import datetime as dt
from random import randrange
from time import sleep

import click

from app.dbapi import (
    create_sensor, get_sensors, create_reading, create_readings, create_user
)
from app.models.users import User


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
    @click.option(
        '--continuous',
        is_flag=True,
        default=False,
        show_default=True,
        help='Send readings continuously, one by one, instead of all at once'
        # TODO: configurable interval for --continuous
    )
    def seed_readings(count, interval, continuous):
        """Seed the database sensors with `count` random readings.

        Starting from `interval` * `count` seconds before now, readings will have
        `interval` seconds between each other.

        If --continuous, then readings will be sent one by one instead.
        """
        all_sensors = get_sensors()
        start_time = dt.datetime.utcnow() - dt.timedelta(seconds=interval*count)

        def get_random_temperature(previous_temperature):
            MAX = 25
            MIN = -25
            result = previous_temperature + randrange(-2_000, 2_000)/1_000
            if result > MAX:
                result = MAX
            elif result < MIN:
                result = MIN
            return result

        if continuous:
            temperatures = [get_random_temperature(0) for _ in all_sensors]
            while True:
                for index, sensor in enumerate(all_sensors):
                    click.echo(
                        f'seeding {temperatures[index]}°C to sensor_id={sensor["id"]}'
                    )
                    create_reading(sensor['id'], temperatures[index])
                    temperatures[index] = get_random_temperature(temperatures[index])
                click.echo('waiting 2s...\n')
                sleep(2)
            return

        for sensor in all_sensors:
            readings = []
            previous_temperature = get_random_temperature(0)
            for times in range(count):
                readings.append(
                    {
                        'sensor_id': sensor['id'],
                        'temperature': previous_temperature,
                        'created_on': start_time + dt.timedelta(seconds=interval*times),
                    }
                )
                previous_temperature = get_random_temperature(previous_temperature)

            create_readings(sensor['id'], readings)

        click.echo(
            f'seeded {count} readings x {len(all_sensors)} sensors'
        )
        total_seeded = len(all_sensors) * count
        click.echo(
            f'total: {total_seeded} readings.'
        )


    @app.cli.command('seed-admin')
    def seed_admin():
        """Seed the database with an admin.

        Display name: "Administrator"; Username: "admin"; password: "default".
        """
        create_user(
            'Administrator', 'admin', 'defaultp', False, User.Permission.ADMIN
        )

        click.echo('created 1 default user. {Administrator|admin|default}')


    @app.cli.command('seed-user')
    def seed_user():
        """Seed the database with a default user.

        Display name: "Felix Sullivan"; Username: "felix"; password: "default".
        """
        create_user(
            'Felix Sullivan',
            'felix',
            'defaultp',
            False,
            User.Permission.MANAGE_REPORTS | User.Permission.EDIT_SENSORS
        )

        click.echo('created 1 default user. {Felix Sullivan|felix|default}')
