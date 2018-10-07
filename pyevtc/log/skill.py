import abc

from . import enum


class Skill:
    def __init__ (self, row):
        self.id_ = row['id']
        self.name = enum.skill.name.get(row['id'], row['name'])

    def __str__ (self):
        return '{}({})'.format(type(self).__name__, repr(self.name))

    __repr__ = __str__

    def __hash__ (self):
        return self.id_

    def __eq__ (self, other):
        return isinstance(other, Skill) and self.id_ == other.id_
