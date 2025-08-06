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
_REPORT_CODE_CHARSET = ascii_lowercase + digits
# 36^10 = approx. 3.6 quadrillion possible codes
_REPORT_CODE_LENGTH = 10
MAX_NOTES_LENGTH = 200


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
    code: str,
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
        code=code,
        formatted_code=format_report_code(code),
        created_on=created_on,
        range_start=range_start,
        range_end=range_end,
        readings=readings,
        total_readings=len(readings),
        data_format=data_format.value,
        notes=notes,
    )


def generate_report_code() -> str:
    """Return a random code of length 10, made of the characters a-z and 0-9."""
    return ''.join(
        random.choices(_REPORT_CODE_CHARSET, k=_REPORT_CODE_LENGTH)
    )


def store_report_file(code: str, content: str):
    """Store the given report content in `REPORTS_DIRECTORY/{code}.html`."""
    with open(path.join(REPORTS_DIRECTORY, f'{code}.html'), 'w') as report:
        report.write(content)


def get_report_file(code: str) -> str:
    """Return the report with the given code."""
    with open(path.join(REPORTS_DIRECTORY, f'{code}.html'), 'r') as report:
        return report.read()


def format_report_code(raw_code: str) -> str:
    """Return the given code in the format XXXX-XXXX-XX, all letters uppercased."""
    uppercased = raw_code.upper()
    return '-'.join(
        (uppercased[0:4], uppercased[4:8], uppercased[8:10])
    )
