from collections import namedtuple
import psutil


START = 'START'
END = 'END'
ConsumedRamLogEntry = namedtuple('ConsumedRamLogEntry', ('nodeid', 'on', 'consumed_ram'))
consumed_ram_log = []


def get_consumed_ram():
    """Gets consumed ram."""
    info = {}
    for proc in psutil.process_iter():
        info.update({proc.name(): (proc.memory_info().rss, proc.memory_info().vms)})
    return info
