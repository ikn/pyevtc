from . import util


class ResultPathIndex:
    def __init__ (self, index):
        self.index = index

    def __str__ (self):
        return str(self.index)


class _Result:
    def __init__ (self, path, value):
        self.path = path
        self.value = value

    def __str__ (self):
        path = '/'.join(str(part) for part in self.path)
        return '{}({}: {})'.format(
            type(self).__name__, repr(path), repr(self.value))

    __repr__ = __str__

    def with_name (self, name):
        return Result((name,) + self.path, self.value)

    def wrap_name (self, name):
        return self.with_name(name) if self.path else self


class _UnnamedResult (_Result):
    def __init__ (self, value):
        _Result.__init__(self, (), value)


class Result (_Result):
    def __init__ (self, path, value):
        _Result.__init__(self, path, value)


class _Part:
    def __init__ (self, read, save=set()):
        self.read = read
        self.save = set(save)


class Definition:
    def __init__ (self, parts):
        self._parts = tuple(parts)

    def __len__ (self):
        return len(self._parts)

    def __iter__ (self):
        return iter(self._parts)

    def __getitem__ (self, i):
        return self._parts[i]

    def __add__ (self, other):
        if other == 0 or (hasattr(other, '__len__') and len(other) == 0):
            return self
        elif not isinstance(other, Definition):
            raise TypeError('cannot add Definition to {}'.format(other))
        else:
            return Definition(self._parts + other._parts)

    def __radd__ (self, other):
        if other == 0 or (hasattr(other, '__len__') and len(other) == 0):
            return self
        else:
            raise TypeError('cannot add Definition to {}'.format(other))

    @property
    def save (self):
        return set().union(*(p.save for p in self))

    def read_iter (self, sr):
        saved = {}

        for part in self:
            pos = sr.pos
            try:
                for result in part.read(saved, sr):
                    if isinstance(result, Result):
                        if result.path in self.save:
                            saved[result.path] = result.value
                        yield result
            except util.WrappedError:
                raise
            except Exception as e:
                raise util.wrap(sr, pos, e)


class RepeatDefinition (Definition):
    def __init__ (self, get_iter, defn, save=set(), ignore_eof=False):
        self._get_iter = get_iter
        self._defn = defn
        self._ignore_eof = ignore_eof
        Definition.__init__(self, (_Part(self._read, set(save)),))

    def _read (self, saved, sr):
        for i, item in enumerate(self._get_iter(saved)):
            try:
                for result in self._defn.read_iter(sr):
                    yield result.wrap_name(ResultPathIndex(i))
            except util.WrappedError as e:
                if isinstance(e.exc, EOFError) and self._ignore_eof:
                    break
                else:
                    raise


empty = Definition(())


def _define (save=set()):
    return lambda read: Definition((_Part(read, save),))


def named (name, defn, result_transform=lambda r: r):
    @_define(defn.save)
    def read (saved, sr):
        for part in defn:
            for result in part.read(saved, sr):
                yield result.with_name(name)
    return read


def const (val):
    @_define()
    def read (results, sr):
        got = sr.read_exactly(len(val))
        if got != val:
            raise util._FormatError(
                'expected to read {}, found {}'.format(val, got))
        return iter(())
    return read


def const_null (length):
    return const(b'\x00' * length)


def parse (length, parser):
    @_define()
    def read (results, sr):
        yield _UnnamedResult(parser(sr.read_exactly(length)))
    return read


def skip (length, check=False):
    @_define()
    def read (results, sr):
        if check:
            sr.read_exactly(length)
        else:
            sr.skip(length)
        return iter(())
    return read


def repeat (length_name, defn):
    get_iter = lambda saved: range(saved[length_name])
    return RepeatDefinition(get_iter, defn, save={length_name})


def repeat_until_eof (defn):
    def get_iter (saved):
        while True:
            yield None

    return RepeatDefinition(get_iter, defn, ignore_eof=True)
