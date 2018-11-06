#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import sys
from optparse import OptionParser


class NagiosRedis(object):

    def __init__(self, host, port, password, bdname):
        self.host = host
        self.password = password
        self.port = port
        self.dbname = bdname

        try:
            self.conn = redis.Redis(host=self.host, port=self.port, password=self.password, socket_timeout=1)
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

    def nagios_check(self):
        number_keys = ''
        version = self.get_version()
        client_connected = self.get_client_connection()
        if self.dbname in str(self.info_out):
            number_keys = self.get_number_keys()
        memory = self.get_used_memory()
        uptime = self.get_uptime()
        if number_keys == '':
            print('OK REDIS No keys, %s, %s, %s' % (version, memory, uptime))
            sys.exit(0)
        else:
            print('OK REDIS %s, %s, %s, %s, %s' % (version, client_connected, number_keys, memory, uptime))
            sys.exit(0)


def build_parser():
    """
    define param command line
    :return: parser config
    """
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-H", "--host", dest="host", help="Redis server to connect to.", default=False)
    parser.add_option("-p", "--port", dest="port", help="Redis port to connect to.", type="int", default=6379)
    parser.add_option("-P", "--password", dest="password", help="Redis password to connect to.",  default='')
    parser.add_option("-d", "--dbname", dest="dbname", help="Redis database name, default is db0", default='db0')
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
        server = NagiosRedis(options.host, options.port, options.password, options.dbname)
        server.nagios_check()
