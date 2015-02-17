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
    st = status.Status(config=config)
    r = st.get_stat(sys.argv[1])
    if r is not False:
        print r
    else:  # 0 for failure
        print 0
    sys.exit(0)

if __name__ == '__main__':
    run()
