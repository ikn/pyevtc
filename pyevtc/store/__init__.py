import itertools
import os
import tempfile
import sqlite3

from . import ingest

_SCHEMA_VERSION = '1'
_ROWS_AT_ONCE = 100


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
        self.path = path

    def quote_identifier (self, ident):
        # sometimes you're just not allowed to use parameter substitution
        return '"' + ident.replace('"', '""') + '"'

    def query (self, sql, params=()):
        c = self._db.cursor()
        c.arraysize = _ROWS_AT_ONCE
        return c.execute(sql, params)

    def name_columns (self, cursor):
        col_names = [col[0] for col in cursor.description]
        for row in cursor:
            yield dict(zip(col_names, row))

    def group_columns (self, cursor, groups_columns):
        tables_cols = [cols for group, cols in groups_columns]
        tables_start = (0,) + tuple(itertools.accumulate(tables_cols))
        total_cols = tables_start[-1]
        col_names = [col[0] for col in cursor.description]

        for row in cursor:
            if len(row) != total_cols:
                raise ValueError(
                    'query returned row with fewer columns than expected:', row,
                    'wanted:', groups_columns)
            grouped_row = {}
            for t_idx, (group, cols) in enumerate(groups_columns):
                start = tables_start[t_idx]
                values = row[start:start + cols]
                # FIXME: is there a more correct way?  (half-empty join)
                if all(v is None for v in values):
                    grouped_row[group] = None
                else:
                    grouped_row[group] = dict(zip(
                        col_names[start:start + cols],
                        row[start:start + cols]))
            yield grouped_row

    def single_row (self, rows):
        try:
            row = next(rows)
        except StopIteration:
            raise ValueError('required data, found none')
        try:
            row_empty = next(rows)
        except StopIteration:
            pass
        else:
            raise ValueError('required one result, found more')
        return row


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
