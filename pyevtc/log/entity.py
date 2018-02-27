import abc

from . import enum


class Entity (metaclass=abc.ABCMeta):
    def __init__ (self, row):
        self.id_ = row['id']
        self.name = row['name']
        self.toughness = row['toughness']
        self.concentration = row['concentration']
        self.healing = row['healing']
        self.condition_damage = row['condition_damage']

    def _str (self, *extra):
        args = (repr(self.name),) + extra
        return '{}({})'.format(type(self).__name__, ', '.join(args))

    def __str__ (self):
        return self._str()

    def __repr__ (self):
        return str(self)


class Player (Entity):
    db_type = 'player'

    def __init__ (self, row):
        Entity.__init__(self, row)
        self.profession = enum.profession.name[row['subtype']]
        self.elite_spec = (
            None if row['player_elite_spec'] is None
            else enum.elite_spec.name[row['player_elite_spec']])
        self.character_name = self.name
        self.account = row['account']
        self.subgroup = row['subgroup']

    def __str__ (self):
        return self._str(
            self.profession if self.elite_spec is None else self.elite_spec)


class NPC (Entity):
    db_type = 'npc'

    def __init__ (self, row):
        Entity.__init__(self, row)
        self.species = row['subtype']

    def __str__ (self):
        return self._str()


class Gadget (Entity):
    db_type = 'gadget'

    def __init__ (self, row):
        Entity.__init__(self, row)
        self.gadget_id = row['subtype']

    def __str__ (self):
        return self._str()


types = [v for v in locals().values()
         if isinstance(v, type) and issubclass(v, Entity) and v is not Entity]
_type_by_db_type = {t.db_type: t for t in types}

def create (row):
    db_type = enum.entity_type.name[row['type']]
    return _type_by_db_type[db_type](row)
