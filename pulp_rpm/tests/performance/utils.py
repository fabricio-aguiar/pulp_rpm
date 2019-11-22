from collections import namedtuple
import pickle
import psutil
import gc
import os
import signal
import threading
import time
import tracemalloc

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


class TakeSnapshot(threading.Thread):
    daemon = True

    def run(self):
        if hasattr(signal, 'pthread_sigmask'):
            # Available on UNIX with Python 3.3+
            signal.pthread_sigmask(signal.SIG_BLOCK, range(1, signal.NSIG))
        counter = 1
        while True:
            time.sleep(30)
            filename = ("/tmp/tracemalloc-%d-%04d.pickle"
                        % (os.getpid(), counter))
            print("Write snapshot into %s..." % filename)
            gc.collect()
            snapshot = tracemalloc.take_snapshot()
            with open(filename, "wb") as fp:
                # Pickle version 2 can be read by Python 2 and Python 3
                pickle.dump(snapshot, fp, 2)
            snapshot = None
            print("Snapshot written into %s" % filename)
            counter += 1
