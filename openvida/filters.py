"""Custom Jinja filter helpers."""

__author__ = "Kestin Goforth"
__copyright__ = "Copyright 2026"
__license__ = "MIT"


def filter_list(src, key, value):
    return filter(lambda t: getattr(t, key) == value, src)


class FilterModule:
    def filters(self):
        return {"byattr": filter_list}
