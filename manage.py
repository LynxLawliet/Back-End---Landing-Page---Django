#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone


def save_landingpage_data(data, output_path='landingpage_data.json'):
    """Guarda los datos de la landing page como registros JSON."""
    path = Path(output_path)
    records = []

    if path.exists():
        try:
            with path.open('r', encoding='utf-8') as file:
                records = json.load(file)
            if not isinstance(records, list):
                records = [records]
        except (json.JSONDecodeError, OSError):
            records = []

    record = dict(data)
    record['created_at'] = record.get(
        'created_at', datetime.now(timezone.utc).isoformat()
    )
    records.append(record)

    with path.open('w', encoding='utf-8') as file:
        json.dump(records, file, ensure_ascii=False, indent=2)

    return path


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()