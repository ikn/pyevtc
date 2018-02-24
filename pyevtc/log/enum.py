import os
import json


class Enum:
    def __init__ (self, name):
        path = os.path.join(os.path.dirname(__file__), 'enum', name + '.json')
        with open(path) as f:
            items = json.load(f)
        self.id_ = {item['name']: item['id'] for item in items}
        self.name = {item['id']: item['name'] for item in items}


# entity
entity_type = Enum('entity-type')
profession = Enum('profession')
elite_spec = Enum('elite-spec')

# skill
skill = Enum('skill')

# event
event_type = Enum('event-type')
state_change = Enum('state-change')
activation_type = Enum('activation-type') # bitmask?
hit_result = Enum('hit-result') # bitmask?
buff_remove = Enum('buff-remove')
team = Enum('team')
