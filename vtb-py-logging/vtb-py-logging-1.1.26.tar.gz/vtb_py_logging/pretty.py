import reprlib

_reprs = {}


class DateTimeRepr(reprlib.Repr):
    def repr_datetime(self, x, level):
        return str(x)

    def repr_time(self, x, level):
        return str(x)

    def repr_date(self, x, level):
        return str(x)


def _explain(config):
    max_item = config.get("maxitem")
    if max_item:
        for prop in ("maxdict", "maxlist", "maxtuple", "maxset", "maxfrozenset", "maxdeque", "maxarray"):
            config.setdefault(prop, max_item)


def get_repr(config, name):
    r = _reprs.get(name)
    if r:
        return r

    r = DateTimeRepr()
    override = config.get(name, {})
    cfg = config["default"].copy()
    _explain(cfg)
    _explain(override)

    cfg.update(override)
    for key, value in cfg.items():
        setattr(r, key, value)
    _reprs[name] = r
    return r

