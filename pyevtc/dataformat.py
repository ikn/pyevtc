from .bytedata import define as d, parse as p

p_uint = p.int_('little')
p_int = p.int_('little', True)


def parse_name (data):
    return tuple(map(p.str_('utf8'),
                     (part for part in data.split(b'\x00') if part)))

defn_entity = sum([
    d.named('id', d.parse(8, p_uint)),
    d.named('profession', d.parse(4, p_uint)),
    d.named('is elite', d.parse(4, p_uint)),
    d.named('toughness', d.parse(2, p_uint)),
    d.named('concentration', d.parse(2, p_uint)),
    d.named('healing', d.parse(2, p_uint)),
    d.named('hitbox width', d.parse(2, p_uint)),
    d.named('condition damage', d.parse(2, p_uint)),
    d.named('hitbox height', d.parse(2, p_uint)),
    d.named('name', d.parse(64, parse_name)),
    d.const_null(4),
])

defn_skill = sum([
    d.named('id', d.parse(4, p_int)),
    d.named('name', d.parse(64, p.null_str('utf8'))),
])

defn_event_v0 = sum([
    d.named('time', d.parse(8, p_uint)),
    d.named('source entity id', d.parse(8, p_uint)),
    d.named('dest entity id', d.parse(8, p_uint)),
    d.named('value', d.parse(4, p_uint)),
    d.named('buff damage', d.parse(4, p_uint)),
    d.named('buff overstack', d.parse(2, p_uint)),
    d.named('skill id', d.parse(2, p_uint)),
    d.named('source entity encounter id', d.parse(2, p_uint)),
    d.named('dest entity encounter id', d.parse(2, p_uint)),
    d.named('source entity owner encounter id', d.parse(2, p_uint)),
    d.skip(9),
    d.named('team', d.parse(1, p_uint)),
    d.named('is buff', d.parse(1, p_uint)),
    d.named('hit result', d.parse(1, p_uint)),
    d.named('is activation', d.parse(1, p_uint)),
    d.named('is buff remove', d.parse(1, p_uint)),
    d.named('health above 90', d.parse(1, p_uint)),
    d.named('health above 50', d.parse(1, p_uint)),
    d.named('is moving', d.parse(1, p_uint)),
    d.named('is state change', d.parse(1, p_uint)),
    d.named('is flanking', d.parse(1, p_uint)),
    d.named('hit barrier', d.parse(1, p_uint)),
    d.skip(2),
])

defn_event_v1 = sum([
    d.named('time', d.parse(8, p_uint)),
    d.named('source entity id', d.parse(8, p_uint)),
    d.named('dest entity id', d.parse(8, p_uint)),
    d.named('value', d.parse(4, p_uint)),
    d.named('buff damage', d.parse(4, p_uint)),
    d.named('buff overstack', d.parse(4, p_uint)),
    d.named('skill id', d.parse(4, p_uint)),
    d.named('source entity encounter id', d.parse(2, p_uint)),
    d.named('dest entity encounter id', d.parse(2, p_uint)),
    d.named('source entity owner encounter id', d.parse(2, p_uint)),
    d.named('dest entity owner encounter id', d.parse(2, p_uint)),
    d.named('team', d.parse(1, p_uint)),
    d.named('is buff', d.parse(1, p_uint)),
    d.named('hit result', d.parse(1, p_uint)),
    d.named('is activation', d.parse(1, p_uint)),
    d.named('is buff remove', d.parse(1, p_uint)),
    d.named('health above 90', d.parse(1, p_uint)),
    d.named('health above 50', d.parse(1, p_uint)),
    d.named('is moving', d.parse(1, p_uint)),
    d.named('is state change', d.parse(1, p_uint)),
    d.named('is flanking', d.parse(1, p_uint)),
    d.named('hit barrier', d.parse(1, p_uint)),
    d.named('alt meaning', d.parse(1, p_uint)),
    d.skip(4),
])

defns_event = {
    0: defn_event_v0,
    1: defn_event_v1,
}

definition = sum([
    d.const(b'EVTC'),
    d.named('arcdps version', d.parse(8, p.str_('ascii'))),
    d.named('arcdps revision', d.parse(1, p_uint)),
    d.named('encounter id', d.parse(2, p_uint)),
    d.const_null(1),
    d.named('num entities', d.parse(4, p_uint)),
    d.named('entities', d.repeat(('num entities',), defn_entity)),
    d.named('num skills', d.parse(4, p_uint)),
    d.named('skills', d.repeat(('num skills',), defn_skill)),
    d.named('events', d.dispatch(
        [('arcdps revision',)],
        lambda rev: d.repeat_until_eof(defns_event[rev]))),
])
