def filter_list(src, key, value):
    return filter(lambda t: getattr(t, key) == value, src)


class FilterModule(object):
    def filters(self):
        return {"byattr": filter_list}
