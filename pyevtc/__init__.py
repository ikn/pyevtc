from . import bytedata, store, dataformat, log


def parse (f):
    sr = bytedata.StreamReader(f, 'stream')
    raw_log = dataformat.definition.read(sr)
    log_store = store.create(raw_log)
    return log.Log(log_store)
