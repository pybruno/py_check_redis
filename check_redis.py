#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import sys
import re
from optparse import OptionParser


class NagiosRedis(object):

    def __init__(self, host, port, username, password, dbname, backup_nodes):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.dbname = dbname
        self.backup_nodes = backup_nodes

        try:
            self.conn = redis.Redis(host=self.host, port=self.port, username=self.username, password=self.password, socket_timeout=1)
            self.info_out = self.conn.info()
            self.conn.ping()

        except Exception as e:
            print('REDIS CRITICAL : ', e)
            sys.exit(2)

    def get_version(self):

        return 'version: %s' % self.info_out['redis_version']

    def get_client_connection(self):

        return 'connected_clients: %d' % self.info_out['connected_clients']

    def get_number_keys(self):

        return self.dbname + ": %d" % self.info_out[self.dbname]['keys']

    def get_uptime(self):

        return "uptime_in_days: %s" % self.info_out['uptime_in_days']

    def get_used_memory(self):

        return "used_memory_human: %s" % self.info_out['used_memory_human']

    def get_role(self):

        return "role: %s" % self.info_out['role']

    def get_connected_backups(self):

        return "connected_backups: %s" % self.info_out['connected_slaves']

    def get_mls(self):

        return "master_link_status: %s" % self.info_out['master_link_status']

    def get_ro(self):

        return "slave_read_only: %s" % self.info_out['slave_read_only']

    def get_master(self):

        return "master_host: %s" % self.info_out['master_host']

    def nagios_check(self):
        number_keys = ''
        version = self.get_version()
        client_connected = self.get_client_connection()
        if self.dbname in str(self.info_out):
            number_keys = self.get_number_keys()
        memory = self.get_used_memory()
        uptime = self.get_uptime()
        role = self.get_role()
        replicas = self.get_connected_backups()
        replica_count = int(re.sub('\D', '', replicas))
        backup_nodes = int(self.backup_nodes)
        if 'master' in role:
            if replica_count != backup_nodes:
                print('REDIS CRITICAL - %s, %s' % (replicas, role))
                sys.exit(2)
        if 'slave' in role:
            mls = self.get_mls()
            ro = self.get_ro()
            master = self.get_master()
            if 'up' not in mls or '1' not in ro:
                print('REDIS CRITICAL - %s, %s, %s, %s' % (role, mls, ro, master))
                sys.exit(2)
        if number_keys == '':
            print('OK REDIS No keys, %s, %s, %s, %s' % (version, memory, uptime, role))
            sys.exit(0)
        else:
            print('OK REDIS %s, %s, %s, %s, %s, %s' % (version, client_connected, number_keys, memory, uptime, role))
            sys.exit(0)


def build_parser():
    """
    define param command line
    :return: parser config
    """
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-H", "--host", dest="host", help="Redis server to connect to.", default='127.0.0.1')
    parser.add_option("-p", "--port", dest="port", help="Redis port to connect to.", type="int", default=6379)
    parser.add_option("-u", "--username", dest="username", help="Redis username.",  default='default')
    parser.add_option("-P", "--password", dest="password", help="Redis password to connect to.",  default='')
    parser.add_option("-d", "--dbname", dest="dbname", help="Redis database name, default is db0", default='db0')
    parser.add_option("-b", "--backup_nodes", dest="backup_nodes", help="Number of connected backup nodes to check for",  default=0)
    parser.add_option("-t", "--timeout", dest="timeout",
                      help="Number of milliesconds to wait before timing out and considering redis down",
                      type="int", default=2000)
    return parser


if __name__ == "__main__":

    parser = build_parser()
    options, args = parser.parse_args()

    if len(args) != 0:
        parser.error("Wrong number of arguments")
        sys.exit(0)

    else:
        server = NagiosRedis(options.host, options.port, options.username, options.password, options.dbname, options.backup_nodes)
        server.nagios_check()
