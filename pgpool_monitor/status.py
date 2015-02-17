import copy
import ConfigParser
import os
import psycopg2
import psycopg2.extras
import subprocess
import sys
import time

DROP_TEMP_TABLE = "DROP TABLE IF EXISTS pgpool_mon;"
CREATE_TEMP_TABLE = "CREATE TEMPORARY TABLE IF NOT EXISTS pgpool_mon (id int);"
WRITE_QUERY = "INSERT INTO pgpool_mon VALUES (1);"
READ_QUERY = 'SELECT 1;'


class Status(object):

    config = None
    connection = None
    cursor = None
    pcp_connection_info = None

    def __init__(self, config):
        self.config = config
        self.connection = self.get_connection()
        self.cursor = self.get_cursor()
        self.pcp_connection_info = self.get_pcp_connection_info()

    def do_read(self):
        try:
            self.cursor.execute(READ_QUERY)
        except:
            return False;
        return True

    def do_write(self):
        try:
            self.cursor.execute(CREATE_TEMP_TABLE)
            self.cursor.execute(WRITE_QUERY)
            self.cursor.execute(DROP_TEMP_TABLE)
        except:
            return False
        return True

    def get_cursor(self):
        self.cursor = self.get_connection().cursor()
        return self.cursor

    def get_connection(self):
        if self.connection is None:
            self.connection = psycopg2.connect(
                host=self.config.get('db', 'host'),
                port=self.config.get('db', 'port'),
                database=self.config.get('db', 'database'),
                user=self.config.get('db', 'user'),
                password=self.config.get('db','password')
            )
        return self.connection

    def get_pcp_connection_info(self):
        if self.pcp_connection_info is None:
            self.pcp_connection_info = [
                self.config.get('pcp', 'timeout'),
                self.config.get('pcp', 'host'),
                self.config.get('pcp', 'port'),
                self.config.get('pcp', 'user'),
                self.config.get('pcp', 'password')
            ]
        return copy.copy(self.pcp_connection_info)

    def run_command(self, command_array):
        """

        :rtype : list
        """
        p = subprocess.Popen(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.wait() == 0:
            return_array = p.stdout.readlines()
        else:
            raise Exception('command failed')
        return return_array

    def do_pcp_node_count(self):
        cmd = self.get_pcp_connection_info()
        cmd.insert(0, 'pcp_node_count')
        try:
            results = self.run_command(cmd)
        except Exception as e:
            print "Error getting count, {e}".format(e=e)
            return False

        return results[0].strip()

    def do_pcp_node_info(self, node_id):
        cmd = self.get_pcp_connection_info()
        cmd.insert(0, 'pcp_node_info')
        cmd.append(str(node_id))
        try:
            results = self.run_command(cmd)
        except Exception as e:
            print "Error getting node info, {e}".format(e=e)
            return False
        
        return results[0].strip()

    def do_pcp_proc_count(self):
        cmd = self.get_pcp_connection_info()
        cmd.insert(0, 'pcp_proc_count')
        try:
            results = self.run_command(cmd)
        except Exception as e:
            print "Error getting proc count, {e}".format(e=e)
            return False
        return results[0].strip()

    def do_pcp_attach_node(self, node_id):
        results = False

        cmd = self.get_pcp_connection_info()
        cmd.insert(0, 'pcp_attach_node')
        cmd.append(str(node_id))

        try:
            self.run_command(cmd)
            time.sleep(1)
            node_info = self.do_pcp_node_info(node_id)
            if node_info is False:
                return False
            info = node_info.split()
            if info[2] in ['1', '2']:
                results = True
        except Exception as e:
            print "Error attaching node, {e}". format(e=e)
            return results
        return results

    def get_total_node_count(self):
        return self.do_pcp_node_count()

    def get_active_node_count(self):
        active_nodes = 0
        total_nodes = self.do_pcp_node_count()
        if total_nodes is False:
            return False
        for x in range(0, int(total_nodes)):
            node_info = self.do_pcp_node_info(x)
            if node_info is False:
                return False
            info = node_info.split()
            if info[2] in ['1', '2']:
                active_nodes += 1
            elif info[2] in ['3']:  # attempt to do a single attach
                if self.do_pcp_attach_node(x) is True:
                    active_nodes += 1
        return active_nodes

    def get_number_procs(self):
        procs = self.do_pcp_proc_count()
        if procs is False:
            return False
        return len(procs.split())

    def get_status_for_zabbix(self, status):
        if status is True:
            return str(1)
        elif status is False:
            return str(0)

        return str(status)

    # main entry point
    # parameter 'stat' is the zabbix name of the stat we want
    def get_stat(self, stat):

        if stat == "READ":
            return self.get_status_for_zabbix(self.do_read())
        elif stat == "WRITE":
            return self.get_status_for_zabbix(self.do_write())
        elif stat == "NODE_COUNT":
            return self.get_total_node_count()
        elif stat == "ACTIVE_COUNT":
            return self.get_active_node_count()
        elif stat == "NUM_PROCS":
            return self.get_number_procs()
        else:
            e = "{status} is not implemented".format(status=stat)
            raise NotImplementedError(e)


if __name__ == '__main__':
    config = ConfigParser.SafeConfigParser()
    config.read([
        '/etc/pgpool_monitor/pgpool_monitor.cfg',
        'pgpool_monitor.cfg',
        os.path.expanduser('~/.pgpool_monitor.cfg'),
        ])
    st = Status(config=config)
    stat = st.get_stat(sys.argv[1])
    print stat
