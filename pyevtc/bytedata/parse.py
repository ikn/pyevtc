import struct


def _until_null (data):
    return data.split(b'\x00')[0]


identity = lambda data: data


def int_ (endian=None, signed=False):
    endian_spec = {None: '@', 'little': '<', 'big': '>'}[endian]

    def parse (data):
        size_spec = {
            1: {False: 'B', True: 'b'},
            2: {False: 'H', True: 'h'},
            4: {False: 'I', True: 'i'},
            8: {False: 'Q', True: 'q'},
        }[len(data)][signed]

        return struct.unpack(endian_spec + size_spec, data)[0]

    return parse


def str_ (enc):
    def parse (data):
        return data.decode(enc)
    return parse


def null_str (enc):
    def parse (data):
        return str_(enc)(_until_null(data))
    return parse
