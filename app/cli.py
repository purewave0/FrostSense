"""Useful CLI commands for populating the database."""

import datetime as dt
from flask import Flask
from random import randrange
from time import sleep

import click

from app.dbapi import (
    create_sensor, get_sensors, get_sensor_ids, get_sensor_by_id, sensor_name_exists,
    delete_sensor_by_id, sensor_id_exists, reset_sensor_key_by_id,
    create_reading, create_readings,
    create_user, get_admin, update_user_password_by_id,
)
from app.models.users import User
from app.models.readings import Sensor


def register_commands(app: Flask):
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

    # -- sensors --

    @app.cli.group()
    def sensor():
        pass

    @sensor.command('create')
    @click.argument('name')
    def cli_create_sensor(name: str) -> None:
        name_length = len(name)
        if (
            name_length < Sensor.MIN_NAME_LENGTH
            or name_length > Sensor.MAX_NAME_LENGTH
        ):
            raise click.UsageError(
                f'sensor names must have {Sensor.MIN_NAME_LENGTH}'
                + f'-{Sensor.MAX_NAME_LENGTH} characters.',
            )

        if sensor_name_exists(name):
            raise click.ClickException('a sensor with that name already exists.')

        sensor = create_sensor(name)
        click.echo(f'created sensor with id={sensor["id"]}.')

    def _format_datetime(datetime: dt.datetime) -> str:
        """Return the given datetime in a human-friendly format."""
        return datetime.strftime("%Y-%m-%d %H:%M")

    @sensor.command('list')
    def cli_list_sensors() -> None:
        sensors = get_sensors()
        click.echo(f'{len(sensors)} sensors in total.')
        # TODO: pretty table?
        click.echo('id | name | created_on')
        for sensor in sensors:
            created_on = _format_datetime(sensor['created_on'])
            click.echo(f'{sensor["id"]} | {sensor["name"]} | {created_on}')

    @sensor.command('delete')
    @click.argument('id')
    def cli_delete_sensor(id: int) -> None:
        if not sensor_id_exists(id):
            raise click.ClickException('no sensor with the given ID.')

        delete_sensor_by_id(id)
        click.echo(f'deleted sensor with id={id}.')

    @sensor.command('show')
    @click.argument('id')
    def cli_show_sensor_info(id: int) -> None:
        if not sensor_id_exists(id):
            raise click.ClickException('no sensor with the given ID.')

        sensor = get_sensor_by_id(id)
        click.echo(f'id: {id}')
        click.echo(f'name: {sensor.name}')
        click.echo(f'key: {sensor.key}')
        click.echo(f'created_on: {sensor.created_on}')

    @sensor.command('reset-key')
    @click.argument('id')
    def cli_reset_sensor_key(id: int) -> None:
        if not sensor_id_exists(id):
            raise click.ClickException('no sensor with the given ID.')

        new_key = reset_sensor_key_by_id(id)
        click.echo(f'reset key of sensor with id={id}.')
        click.echo(f'new key: {new_key}')

    @sensor.command('seed')
    @click.option(
        '--count',
        type=int,
        default=4,
        show_default=True,
        help='How many sensors to add'
    )
    def seed_sensors(count):
        """Seed the database with the given amount of sensors."""

        current_sensors_count = len(get_sensor_ids())
        for number in range(
            current_sensors_count+1, current_sensors_count+count+1
        ):
            click.echo(f'creating "Sensor {number}"')
            create_sensor(f'Sensor {number}')

        click.echo(f'seeded {count} sensors.')

    # -- admin --

    @app.cli.group()
    def admin():
        pass

    @admin.command('reset-password')
    def cli_reset_admin_password() -> None:
        admin = get_admin()
        if not admin:
            raise click.ClickException("the admin account hasn't been created.")

        temporary_password = User.generate_temporary_password()
        update_user_password_by_id(admin.id, temporary_password, True)
        click.echo('reset the admin password.')
        click.echo(f'new temporary password: {temporary_password}')
