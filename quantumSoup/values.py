from datetime import datetime, timezone

class BaseValue(object):

    __slots__ = "_tuple"

    _fields = "value"
    _optional = True

    _timeFormat = None

    def __init__(self, value=None):
        self._tuple = (value,)

    @classmethod
    def keys(cls):
        return cls._fields

    def values(self, iso8601=False):
        return self._astuple(iso8601)

    def _astuple(self, iso8601=False):
        if iso8601:
            return tuple(
                (
                    value.isoformat()
                    if isinstance(value, datetime)
                    else value
                )
                for value, optional in zip(self._tuple, self._optional)
                if not optional or not (value is None)
            )
        else:
            return tuple(
                value
                for value, optional in zip(self._tuple, self._optional)
                if not optional or not (value is None)
            )

    def _asdict(self, iso8601=False):
        return dict(zip(self._fields, self._astuple(iso8601)))

    def __getitem__(self, key):
        try:
            return self._tuple[key]
        except (TypeError, IndexError):
            return self._tuple[self._ixLookup[key]]

    def __iter__(self):
        return iter(self._astuple())

    def __repr__(self):
        return repr(self._asdict(iso8601=True))

    # Some time helper / coersion bits.
    # Don't try to need this: just use ISO8601 for your date format like Canary does:
    #  YYYY-MM-DD HH:mm:ss.SSSSSSZ
    def setTimeFormat(self, formatString):
        self._timeFormat = formatString

    def _coerceTimestamp(self, timestamp):
        if isinstance(timestamp, str):
            # A timestamp on Christ's Epoch should be understood as an error.
            # It's not a real time, so return None. It's essentially a soft error.
            # Since it's _not_ a timestamp, we'll return None.
            if timestamp.startswith("0001-01-01"):
                return None

            if self._timeFormat:
                return datetime.strptime(timestamp, self._timeFormat)

            try:  # the iso8601 format first
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError(
                    f'{self!r} attempted to parse "{timestamp}" without a time format'
                )

        # if it's already a datetime converto to this more convenient class
        elif isinstance(timestamp, datetime):
            return timestamp

        # if it's a tuple (like what would be used ot initialize a datetime), then init
        elif isinstance(timestamp, (tuple, list)):
            return datetime(*timestamp)

        else:
            try:  # see if arrow can convert it anyhow (like ms since epoch...)
                return datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
            except ValueError:
                raise ValueError(
                    f'{self!r} attempted to parse "{timestamp}" without a time format'
                )


def _finalize(BVClass, aliases=None):
    setattr(
        BVClass,
        "_ixLookup",
        dict((field, ix) for ix, field in enumerate(BVClass._fields)),
    )
    for ix, key in enumerate(BVClass._fields):
        setattr(BVClass, key, property(lambda self, ix=ix: self._tuple[ix]))
        setattr(
            BVClass, "get%s" % key.capitalize(), lambda self, ix=ix: self._tuple[ix]
        )
    if aliases:
        for ix, key in enumerate(aliases):
            setattr(BVClass, key, property(lambda self, ix=ix: self._tuple[ix]))


class Tvq(BaseValue):
    _fields = ("timestamp", "value", "quality")
    _optional = (False, False, True)

    def __init__(self, timestamp, value, quality=None):
        timestamp = self._coerceTimestamp(timestamp)

        self._tuple = (timestamp, value, quality)


_finalize(Tvq, "t v q".split())


class Property(BaseValue):
    _fields = ("name", "timestamp", "value", "quality")
    _optional = (False, False, False, True)

    def __init__(self, name, timestamp, value, quality=None):
        timestamp = self._coerceTimestamp(timestamp)

        self._tuple = (name, timestamp, value, quality)


_finalize(Property, "n t v q".split())


class Annotation(BaseValue):
    _fields = ("user", "timestamp", "value", "createdAt")
    _optional = (False, False, False, True)

    def __init__(self, user, timestamp, value, createdAt=None):
        timestamp = self._coerceTimestamp(timestamp)
        if createdAt:
            createdAt = self._coerceTimestamp(createdAt)
        self._tuple = (user, timestamp, value, createdAt)


_finalize(Annotation, "u t v c".split())


VALUE_TYPE_MAP = {"tvq": Tvq, "property": Property, "annotation": Annotation}


def createValue(valueType="tvq", *values):
    return VALUE_TYPE_MAP[valueType.lower()](*values)
