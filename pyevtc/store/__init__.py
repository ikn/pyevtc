import os
import tempfile
import sqlite3

from . import ingest

_SCHEMA_VERSION = '1'


def _load_schema (db):
    path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(path) as f:
        sql = f.read()
    db.executescript(sql)


def _iter_log_sectioned (raw_log, separators):
    seps_iter = iter(separators)
    next_sep = next(seps_iter)
    for item in raw_log:
        if item.path[0] == next_sep:
            yield None
            try:
                next_sep = next(seps_iter)
            except StopIteration:
                next_sep = None
        yield item


def _iter_section (iter_):
    for item in iter_:
        if item is None:
            break
        else:
            yield item


def _load_data (raw_log, db):
    raw_log_sectioned = _iter_log_sectioned(
        raw_log, ('entities', 'skills', 'events'))

    db.executemany(ingest.metadata_sql,
                   ingest.metadata_params(_iter_section(raw_log_sectioned),
                                          _SCHEMA_VERSION))
    ingest.many(_iter_section(raw_log_sectioned), db, 'entities')
    ingest.many(_iter_section(raw_log_sectioned), db, 'skills')
    ingest.many(_iter_section(raw_log_sectioned), db, 'events')


class Store:
    def __init__ (self, db, path):
        self._db = db
        db.row_factory = sqlite3.Row
        self.path = path

    def query (self, sql, params=()):
        return self._db.execute(sql, params)


def create (raw_log, disk=False, path=None):
    if disk and path is None:
        fd, path = tempfile.mkstemp()
        os.close(fd)
    db = sqlite3.connect(path if disk else ':memory:')

    _load_schema(db)
    _load_data(raw_log, db)
    db.commit()

    return Store(db, path)


def load (path):
    return Store(sqlite3.connect(path), path)
