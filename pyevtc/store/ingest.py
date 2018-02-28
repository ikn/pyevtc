from .. import bytedata, log

metadata_sql = 'INSERT INTO `metadata` (`name`, `value`) VALUES (?, ?)'

def metadata_params (raw_log_section, schema_version):
    yield ('pyevtc schema version', schema_version)
    for item in raw_log_section:
        if item.path == ('arcdps version',):
            yield ('arcdps version', item.value)
        elif item.path == ('encounter id',):
            yield ('encounter id', str(item.value))


many_defn = {'entities': {}, 'skills': {}, 'events': {}}


many_defn['entities']['sql'] = '''
    INSERT INTO `entities` (
        `type`,
        `subtype`,
        `player_elite_spec`,
        `id`,
        `name`,
        `account`,
        `subgroup`,
        `toughness`,
        `concentration`,
        `healing`,
        `condition_damage`
    ) VALUES (
        :type,
        :subtype,
        :player_elite_spec,
        :id,
        :name,
        :account,
        :subgroup,
        :toughness,
        :concentration,
        :healing,
        :condition_damage
    )
'''

def transform_entity (e):
    type_id = log.enum.entity_type.id_

    if e['is elite'] == 0xffffffff:
        subtype = e['profession'] & 0xffff
        player_elite_spec = None
        if (e['profession'] << 4) == 0xffff:
            type_ = type_id['gadget']
            # subtype is gadget ID
        else:
            type_ = type_id['npc']
            # subtype is species
    else:
        type_ = type_id['player']
        subtype = e['profession']
        player_elite_spec = None if e['is elite'] == 0 else e['is elite']

    return {
        'type': type_,
        'subtype': subtype,
        'player_elite_spec': player_elite_spec,
        'id': hash(e['id']),
        'name': e['name'][0],
        'account': e['name'][1] if type_ == type_id['player'] else None,
        'subgroup': e['name'][2] if type_ == type_id['player'] else None,
        'toughness': e['toughness'],
        'concentration': e['concentration'],
        'healing': e['healing'],
        'condition_damage': e['condition damage'],
    }

many_defn['entities']['fields'] = transform_entity


many_defn['skills']['sql'] = '''
    INSERT INTO `skills` (`id`, `name`) VALUES (:id, :name)
'''

def transform_skill (s):
    return {
        'id': hash(s['id']),
        'name': s['name'],
    }

many_defn['skills']['fields'] = transform_skill


many_defn['events']['sql'] = '''
    INSERT INTO `events` (
        `type`,
        `subtype`,
        `time`,
        `source_entity_id`,
        `dest_entity_id`,
        `skill_id`,
        `value`,
        `team`,
        `hit_result`,
        `hit_barrier`
    ) VALUES (
        :type,
        :subtype,
        :time,
        :source_entity_id,
        :dest_entity_id,
        :skill_id,
        :value,
        :team,
        :hit_result,
        :hit_barrier
    )
'''

def transform_event (e):
    value = e['value']
    hit_result = e['hit result']

    type_id = log.enum.event_type.id_
    if e['is state change']:
        type_ = type_id['state change']
        subtype = e['is state change']
    elif e['is activation']:
        type_ = type_id['activation']
        subtype = e['is activation']
    elif e['is buff remove']:
        type_ = type_id['buff']
        subtype = e['is buff remove']
    elif e['is buff']:
        if value == 0:
            type_ = type_id['damage']
            subtype = log.enum.damage_type.id_['condition']
            value = e['buff damage']
            hit_result = (log.enum.hit_result.id_['absorbed']
                          if value == 0 else log.enum.hit_result.id_['normal'])
        else:
            type_ = type_id['buff']
            subtype = log.enum.buff_type.id_['apply']
    else:
        type_ = type_id['damage']
        subtype = log.enum.damage_type.id_['power']

    return {
        'type': type_,
        'subtype': subtype,
        'time': e['time'],
        'source_entity_id': hash(e['source entity id']),
        'dest_entity_id': hash(e['dest entity id']),
        'skill_id': hash(e['skill id']),
        'value': value,
        'team': e['team'],
        'hit_result': hit_result,
        'hit_barrier': e['hit barrier'],
    }

many_defn['events']['fields'] = transform_event


def many_params (raw_log, group_name):
    item_index = None
    item = {}

    def finish_item ():
        if item_index is None:
            return ()
        else:
            return (many_defn[group_name]['fields'](item),)

    for field in raw_log:
        if (
            len(field.path) == 3 and
            field.path[0] == group_name and
            isinstance(field.path[1], bytedata.define.ResultPathIndex) and
            isinstance(field.path[2], str)
        ):
            this_index = field.path[1].index
            if this_index != item_index:
                yield from finish_item()
                item_index = this_index
                item = {}
            item[field.path[2]] = field.value

    yield from finish_item()


def many (raw_log, db, group_name):
    db.executemany(
        many_defn[group_name]['sql'],
        many_params(raw_log, group_name))
