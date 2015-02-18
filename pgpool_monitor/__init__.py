#!/usr/bin/python

import ConfigParser
import os
import sys

from . import status


def run():
    config = ConfigParser.SafeConfigParser()
    config.read([
        '/etc/pgpool_monitor.cfg',
        'pgpool_monitor.cfg',
        os.path.expanduser('~/.pgpool_monitor.cfg'),
        ])
    return_code = 0
    if len(sys.argv) < 2:
        print """Usage: pgpool_monitor <stat>
        Valid stats:
        - READ
        - WRITE
        - NODE_COUNT
        - ACTIVE_COUNT
        - NUM_PROCS
        """
        sys.exit(1)

    try:
        st = status.Status(config=config)
        r = st.get_stat(sys.argv[1])
        if r is not False:
            print r
        else:  # 0 for failure
            print 0
    except Exception as e:
        print "Error, {s}".format(s=e)
        return_code = 1
    sys.exit(return_code)

if __name__ == '__main__':
    run()
