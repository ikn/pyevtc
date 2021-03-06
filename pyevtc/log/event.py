from . import enum, entity, skill


class Event:
    db_type = None
    # must be None if there's no entry in `db_subtype_enum` for `db_type`
    db_subtype = None

    def __init__ (self, row):
        self.time = row['event']['time']
        self.source_entity = (None if row['source entity'] is None
                              else entity.create(row['source entity']))
        self.dest_entity = (None if row['dest entity'] is None
                            else entity.create(row['dest entity']))

    def _str (self, extra=None):
        if extra is None and self.source_entity is not None:
            extra = str(self.source_entity)
        if extra is None:
            return '{}(@{})'.format(type(self).__name__, self.time)
        else:
            return '{}(@{}: {})'.format(type(self).__name__, self.time, extra)

    def __str__ (self):
        return self._str()

    def __repr__ (self):
        return str(self)


class StateChangeEvent (Event):
    db_type = 'state change'

    def __init__ (self, row):
        Event.__init__(self, row)


class EnterCombatEvent (StateChangeEvent):
    db_subtype = 'enter combat'
class ExitCombatEvent (StateChangeEvent):
    db_subtype = 'exit combat'
class UpEvent (StateChangeEvent):
    db_subtype = 'up'
class DeadEvent (StateChangeEvent):
    db_subtype = 'dead'
class DownedEvent (StateChangeEvent):
    db_subtype = 'downed'
class SpawnEvent (StateChangeEvent):
    db_subtype = 'spawn'
class DespawnEvent (StateChangeEvent):
    db_subtype = 'despawn'


class HealthEvent (StateChangeEvent):
    db_subtype = 'health'

    def __init__ (self, row):
        StateChangeEvent.__init__(self, row)
        self.health = row['event']['dest_entity_id'] / 10000

    def __str__ (self):
        return self._str('{} -> {}'.format(self.source_entity, self.health))


class WeaponSwapEvent (StateChangeEvent):
    db_subtype = 'weapon swap'

    def __init__ (self, row):
        StateChangeEvent.__init__(self, row)
        self.weapon_set = enum.weapon_set.name[row['event']['dest_entity_id']]


class MaxHealthEvent (StateChangeEvent):
    db_subtype = 'max health'

    def __init__ (self, row):
        StateChangeEvent.__init__(self, row)
        self.max_health = row['event']['dest_entity_id']

    def __str__ (self):
        return self._str('{} -> {}'.format(self.source_entity, self.max_health))


class ActivationEvent (Event):
    db_type = 'activation'

    def __init__ (self, row):
        Event.__init__(self, row)
        self.source_entity = (None if row['source entity'] is None
                              else entity.create(row['source entity']))
        self.skill = skill.Skill(row['skill'])
        self.cast_time = row['event']['value'] / 1000

    def __str__ (self):
        return self._str(str(self.skill))


class NormalActivationEvent (ActivationEvent):
    db_subtype = 'normal'
class QuicknessActivationEvent (ActivationEvent):
    db_subtype = 'quickness'
class CancelChannelEvent (ActivationEvent):
    db_subtype = 'cancel-channel'
class CancelCastEvent (ActivationEvent):
    db_subtype = 'cancel-cast'
class CompleteActivationEvent (ActivationEvent):
    db_subtype = 'complete'


class DamageEvent (Event):
    db_type = 'damage'

    def __init__ (self, row):
        Event.__init__(self, row)
        self.skill = skill.Skill(row['skill'])
        self.team = enum.team.name[row['event']['team']]
        self.damage = row['event']['value']
        self.result = enum.hit_result.name[row['event']['hit_result']]
        self.mitigated = self.result in (
            'blocked', 'evaded', 'absorbed', 'blinded'
        )
        self.hit_barrier = bool(row['event']['hit_barrier'])

    def __str__ (self):
        return self._str('{} {} {}'.format(
            self.skill, self.result, self.damage))


class PowerDamageEvent (DamageEvent):
    db_subtype = 'power'
class ConditionDamageEvent (DamageEvent):
    db_subtype = 'condition'


class BuffEvent (Event):
    db_type = 'buff'

    def __init__ (self, row):
        Event.__init__(self, row)
        self.skill = skill.Skill(row['skill'])
        self.team = enum.team.name[row['event']['team']]

    def __str__ (self):
        return self._str(str(self.skill))


class BuffApplyEvent (BuffEvent):
    db_subtype = 'apply'

    def __init__ (self, row):
        BuffEvent.__init__(self, row)
        self.duration = row['event']['value'] / 1000


class BuffRemoveAllStacksEvent (BuffEvent):
    db_subtype = 'remove all stacks'
class BuffRemoveStackEvent (BuffEvent):
    db_subtype = 'remove single stack'
class BuffResetEvent (BuffEvent):
    db_subtype = 'reset'


types = [v for v in locals().values()
         if isinstance(v, type) and issubclass(v, Event)]
_type_by_db_type = {(t.db_type, t.db_subtype): t for t in types}

db_subtype_enums = {
    'state change': enum.state_change_type,
    'activation': enum.activation_type,
    'damage': enum.damage_type,
    'buff': enum.buff_type,
}

def create (row):
    db_type = enum.event_type.name[row['event']['type']]
    db_subtype_enum = db_subtype_enums.get(db_type)
    db_subtype = (None if db_subtype_enum is None
                  else db_subtype_enum.name[row['event']['subtype']])

    type_ = next(t for t in (
        _type_by_db_type.get((db_type, db_subtype)),
        _type_by_db_type.get((db_type, None)),
        _type_by_db_type.get((None, None))
    ) if t)
    return type_(row)
