from . import entity, skill, event

_SUPPORTED_SCHEMA_VERSIONS = ['1']


class Log:
    def __init__ (self, store):
        self._store = store
        self._table_columns = {'metadata': 2}
        self._schema_version = self._query_metadata('pyevtc schema version')
        if self._schema_version not in _SUPPORTED_SCHEMA_VERSIONS:
            raise ValueError(
                'store has unsupported schema version:', self._schema_version)
        self._update_table_columns(['entities', 'skills', 'events'])

    def _update_table_columns (self, tables):
        for table in tables:
            quoted_table = self._store.quote_identifier(table)
            cursor = self._store.query(
                'SELECT * FROM ' + quoted_table + ' LIMIT 1')
            self._table_columns[table] = len(cursor.description)

    def _group_columns (self, cursor, groups):
        groups_columns = [(group, self._table_columns[table])
                          for group, table in groups]
        return self._store.group_columns(cursor, groups_columns)

    def _query_metadata(self, name):
        row = self._store.single_row(self._store.name_columns(self._store.query(
            'SELECT * FROM "metadata" WHERE "name" = ?', [name])))
        return row['value']

    @property
    def arcdps_version (self):
        return self._query_metadata('arcdps version')

    @property
    def encounter_id (self):
        return self._query_metadata('encounter_id')

    def entities (self, types=None):
        if types is None:
            where_clause = ''
            params = []
        else:
            where_clause = 'WHERE ' + ' OR '.join('"type" = ?' for t in types)
            params = [enum.entity_type.id_[t.db_type] for t in types]

        sql = 'SELECT * from "entities" ' + where_clause
        for row in self._store.name_columns(self._store.query(sql, params)):
            yield entity.create(row)

    @property
    def skills (self):
        sql = 'SELECT * FROM "skills"'
        for row in self._store.name_columns(self._store.query(sql)):
            yield skill.Skill(row['skills'])

    def events (self, types=None):
        if types is None or not types:
            where_clause = ''
            params = []
        else:
            cases = []
            params = []
            for t in types:
                if t.db_type is None:
                    cases.append('1')
                elif t.db_subtype is None:
                    cases.append('"ev"."type" = ?')
                    params.append(enum.event_type.id_[t.db_type])
                else:
                    cases.append('("ev"."type" = ? AND "ev"."subtype" = ?)')
                    params.append(enum.event_type.id_[t.db_type])
                    db_subtype_enum = event.db_subtype_enums[t.db_type]
                    params.append(db_subtype_enum.id_[t.db_subtype])
            where_clause = 'WHERE ' + ' OR '.join(cases)

        sql = '''
            SELECT "ev".*, "se".*, "de".*, "s".*
            FROM "events" AS "ev"
            LEFT JOIN "entities" AS "se" ON "se"."id" = "ev"."source_entity_id"
            LEFT JOIN "entities" AS "de" ON "de"."id" = "ev"."dest_entity_id"
            INNER JOIN "skills" AS "s" ON "s"."id" = "ev"."skill_id"
            {}
            ORDER BY "ev"."time" ASC
        '''.format(where_clause)
        cursor = self._store.query(sql, params)

        for row in self._group_columns(cursor, [
            ('event', 'events'),
            ('source entity', 'entities'),
            ('dest entity', 'entities'),
            ('skill', 'skills'),
        ]):
            yield event.create(row)
