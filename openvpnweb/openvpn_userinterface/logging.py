# encoding: utf-8
# vim: shiftwidth=4 expandtab

from .models import LogEntry

def log(*args, **kwargs):
    # TODO make sure this gets committed even if txn block is rollback'd
    entry = LogEntry(*args, **kwargs)
    entry.save()
    return entry 
