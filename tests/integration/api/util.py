from datetime import datetime


def _parsed_datetime(created_on: str):
    """Return the given 'YYYY-MM-DDThh:mm:ssZ' datetime string as a datetime object."""
    return datetime.strptime(created_on, '%Y-%m-%dT%H:%M:%SZ')
