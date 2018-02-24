class WrappedError (Exception):
    def __init__ (self, sr, sr_pos, exc):
        Exception.__init__(self)
        self.sr = sr
        self.sr_pos = sr_pos
        self.exc = exc

    def __str__ (self):
        return '{}: {}:0x{:x}: {}'.format(
            type(self.exc).__name__, self.sr.name, self.sr_pos, str(self.exc))

    def __repr__ (self):
        return '{}({})'.format(type(self.exc).__name__, repr(str(self)))


class WrappableError (Exception):
    pass


class WrappedWrappableError (WrappedError):
    def __str__ (self):
        return '{}:0x{:x}: {}'.format(self.sr.name, self.sr_pos, str(self.exc))

    def __repr__ (self):
        return '{}({})'.format(type(self).__name__, repr(str(self)))


class FormatError (WrappedWrappableError):
    def __init__ (self, sr, sr_pos, fmt_err):
        WrappedError.__init__(self, sr, sr_pos, fmt_err)


class _FormatError (WrappableError):
    wrap_cls = FormatError

    def __init__ (self, msg):
        WrappableError.__init__(self, 'format error: {}'.format(msg))


def wrap (sr, sr_pos, exc):
    cls = exc.wrap_cls if isinstance(exc, WrappableError) else WrappedError
    return cls(sr, sr_pos, exc)
