from collections.abc import Collection
from datetime import datetime
from enum import Enum
from os import path
import random
from string import ascii_lowercase, digits
from typing import Any

from flask import render_template


REPORTS_DIRECTORY = path.join('app', 'generated_reports')
# a-z + 0-9 = 36 characters
_TOKEN_CHARSET = ascii_lowercase + digits
# 36^10 = approx. 3.6 quadrillion possible tokens
_TOKEN_LENGTH = 10


class DataFormat(Enum):
    """How the readings should be displayed in the report."""
    TABLE = 'table'
    """Display them in a table. Columns: datetime, temperature. If there are too many
        readings, the table may wrap around to the right."""
    GRAPH = 'graph'
    """Display them in a graph. Y axis: datetime; X axis: temperature."""
    TABLE_AND_GRAPH = 'table-and-graph'
    """Display them in a table and a graph at the same time."""


def generate_report_html(
    sensor_name: str,
    token: str,
    created_on: datetime,
    range_start: datetime,
    range_end: datetime,
    readings: Collection[dict[str, Any]],
    data_format: DataFormat,
    notes: str | None
) -> str:
    """Return the generated HTML of a report containing the given data."""
    return render_template(
        'report/template.html',
        sensor_name=sensor_name,
        token=token,
        formatted_token=format_token(token),
        created_on=created_on,
        range_start=range_start,
        range_end=range_end,
        readings=readings,
        total_readings=len(readings),
        data_format=data_format.value,
        notes=notes,
    )


def generate_token() -> str:
    """Return a random token of length 10, made of the characters a-z and 0-9."""
    return ''.join(
        random.choices(_TOKEN_CHARSET, k=_TOKEN_LENGTH)
    )


def store_report_file(token: str, content: str):
    """Store the given report content in `REPORTS_DIRECTORY/{token}.html`."""
    with open(path.join(REPORTS_DIRECTORY, f'{token}.html'), 'w') as report:
        report.write(content)


def get_report_file(token: str) -> str:
    """Return the report with the given token."""
    with open(path.join(REPORTS_DIRECTORY, f'{token}.html'), 'r') as report:
        return report.read()


def format_token(raw_token: str) -> str:
    """Return the given token in the format XXXX-XXXX-XX, all letters uppercased."""
    uppercased = raw_token.upper()
    return '-'.join(
        (uppercased[0:4], uppercased[4:8], uppercased[8:10])
    )
