from setuptools import setup
from sys import path

path.insert(0, '.')

NAME = "pgpool_monitor"

if __name__ == "__main__":

    setup(
        name = NAME,
        version = "0.1.0",
        author = "Alex Schultz",
        author_email = "alex.schultz@rackspace.com",
        url = "https://github.rackspace.com/cloud-integration-ops/pgpool-monitor",
        license = 'internal use',
        packages = [NAME],
        package_dir = {NAME: NAME},
        data_files = [ ('/etc', ['pgpool_monitor.cfg']) ],
        description = "Send pgpool status to Zabbix",

        entry_points={
            'console_scripts': [ 'pgpool_monitor = pgpool_monitor:run' ],
        }
    )

