"""Helper utilities and decorators."""

from flask import flash
from sqlalchemy.orm import sessionmaker


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text} - {error}", category)


def compress_years(years):
    """Convert list of years to range strings like '2001-2003, 2005'"""
    if not years:
        return ""

    # Expand any existing ranges in the input
    expanded_years = set()
    for item in years:
        if isinstance(item, str) and "-" in item:
            parts = item.split("-")
            if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                start_year = int(parts[0].strip())
                end_year = int(parts[1].strip())
                expanded_years.update(range(start_year, end_year + 1))
            else:
                try:
                    expanded_years.add(int(item))
                except (ValueError, TypeError):
                    pass
        else:
            try:
                expanded_years.add(int(item))
            except (ValueError, TypeError):
                pass

    sorted_years = sorted(expanded_years)
    if not sorted_years:
        return ""
    ranges = []
    start = sorted_years[0]
    end = sorted_years[0]
    for year in sorted_years[1:]:
        if year == end + 1:
            end = year
        else:
            ranges.append(f"{start}-{end}" if start != end else str(start))
            start = year
            end = year
    ranges.append(f"{start}-{end}" if start != end else str(start))
    return ", ".join(ranges)


def with_session(session_type: sessionmaker):
    def decorator(func):
        def wrapper(*a, session: sessionmaker = None):
            if session is None:
                with session_type() as session_:
                    return func(*a, session=session_)
            else:
                return func(*a, session=session)

        return wrapper

    return decorator
