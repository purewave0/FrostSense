from datetime import datetime
import re


def parsed_datetime(created_on: str):
    """Return the given 'YYYY-MM-DDThh:mm:ssZ' datetime string as a datetime object."""
    return datetime.strptime(created_on, '%Y-%m-%dT%H:%M:%SZ')

temporary_password_pattern = re.compile(r'[a-z0-9]{12}')
"""The format for temporary user passwords."""

avatar_hex_colour_pattern = re.compile(r'#[a-f0-9]{6}')
"""The hex format for users' avatar colours."""
