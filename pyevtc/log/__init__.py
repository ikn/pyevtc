import abc

from . import enum

_SUPPORTED_SCHEMA_VERSIONS = ['1']


class Entity (metaclass=abc.ABCMeta):
    def __init__ (self, record):
        self.id_ = record['id']
        self.name = record['name']
        self.toughness = record['toughness']
        self.concentration = record['concentration']
        self.healing = record['healing']
        self.condition_damage = record['condition_damage']

    def _str (self, *extra):
        args = (repr(self.name),) + extra
        return '{}({})'.format(type(self).__name__, ', '.join(args))

    def __str__ (self):
        return self._str()

    def __repr__ (self):
        return str(self)


class Player (Entity):
    def __init__ (self, record):
        Entity.__init__(self, record)
        self.profession = enum.profession.name[record['subtype']]
        self.elite_spec = (
            None if record['player_elite_spec'] is None
            else enum.elite_spec.name[record['player_elite_spec']])
        self.character_name = self.name
        self.account = record['account']
        self.subgroup = record['subgroup']
        self.name += self.account

    def __str__ (self):
        return self._str(
            self.profession if self.elite_spec is None else self.elite_spec)


class NPC (Entity):
    def __init__ (self, record):
        Entity.__init__(self, record)
        self.species = record['subtype']

    def __str__ (self):
        return self._str(str(self.species))


class Gadget (Entity):
    def __init__ (self, record):
        Entity.__init__(self, record)
        self.gadget_id = record['subtype']

    def __str__ (self):
        return self._str(str(self.gadget_id))


def mk_entity (record):
    type_ = enum.entity_type.name[record['type']]
    cls = {
        'player': Player,
        'npc': NPC,
        'gadget': Gadget
    }[type_]
    return cls(record)


class Skill:
    def __init__ (self, record):
        self.id_ = record['id']
        self.name = enum.skill.name.get(record['id'], record['name'])

    def __str__ (self):
        return '{}({})'.format(type(self).__name__, repr(self.name))

    __repr__ = __str__


class Event:
    def __init__ (self):
        self.time = None
        self.source_entity = None
        self.dest_entity = None
        self.skill = None

    def __str__ (self):
        return '[{}]'.format(self.time)

    def __repr__ (self):
        return '[{}: {}/{} -> {}]'.format(
            self.time, self.source_entity, self.skill, self.dest_entity)


class Log:
    def __init__ (self, store):
        self._store = store
        self._schema_version = self._query_metadata('pyevtc schema version')
        if self._schema_version not in _SUPPORTED_SCHEMA_VERSIONS:
            raise ValueError(
                'store has unsupported schema version:', self._schema_version)

    def _query_require (self, sql, params=()):
        c = self._store.query(sql, params)
        record = c.fetchone()
        if record is None:
            raise ValueError('required data, found none')
        record_empty = c.fetchone()
        if record_empty is not None:
            raise ValueError('required one result, found more')
        return record

    def _query_metadata(self, name):
        record = self._query_require(
            'SELECT * FROM `metadata` WHERE `name` = ?', (name,))
        return record['value']

    @property
    def arcdps_version (self):
        return self._query_metadata('arcdps version')

    @property
    def encounter_id (self):
        return self._query_metadata('encounter_id')

    def _entities (self, where_clause, params):
        query = 'SELECT * from `entities`'
        for record in self._store.query(query + ' ' + where_clause, params):
            yield mk_entity(record)

    @property
    def entities (self):
        return self._entities('', ())

    @property
    def players (self):
        return self._entities('WHERE `type` = ?',
                              (enum.entity_type.id_['player'],))

    @property
    def npcs (self):
        return self._entities('WHERE `type` = ?',
                              (enum.entity_type.id_['npc'],))

    @property
    def gadgets (self):
        return self._entities('WHERE `type` = ?',
                              (enum.entity_type.id_['gadget'],))

    @property
    def skills (self):
        for record in self._store.query('SELECT * from `skills`'):
            yield Skill(record)

    # TODO: events
