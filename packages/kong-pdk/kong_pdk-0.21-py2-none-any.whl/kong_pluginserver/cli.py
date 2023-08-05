#!/usr/bin/env python
# coding:utf-8
# Contributor:
#      fffonion        <fffonion@gmail.com>

import os
import sys
import argparse
import traceback
import msgpack
import json

from . import PluginServer
from .server import UnixStreamServer
from .logger import Logger

from .const import __version__, PY3K

def parse(dedicated=False):
    parser = argparse.ArgumentParser(description='Kong Python Plugin Server.')
    parser.add_argument('-p', '--kong-prefix', '-kong-prefix',
                        dest='prefix', metavar='prefix', type=str,
                        default="/usr/local/kong/",
                        help='Unix domain socket path to listen')
    parser.add_argument('-v', '--verbose', action='count', default = Logger.INFO,
                        help='Turn on verbose logging')
    parser.add_argument('--version', '-version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))

    if not dedicated:
        parser.add_argument('-d', '--plugins-directory', '-plugins-directory',
                            dest='directory', metavar='directory', type=str, required=True,
                            help='Plugins directory')
        parser.add_argument('--dump-plugin-info', '-dump-plugin-info', dest='dump_info', metavar='name', type=str,
                            help='Dump specific plugin info into stdout')
        parser.add_argument('--dump-all-plugins', '-dump-all-plugins', dest='dump_all_info', action="store_true",
                            help='Dump specific plugin info into stdout')
    else:
        parser.add_argument('--dump', '-dump', dest='dump', action="store_true",
                            help='Dump plugin info into stdout')

    args = parser.parse_args()
    return args

def start():
    args = parse()

    prefix = args.prefix
    if not os.path.exists(prefix):
        raise OSError("path %s doesn't exist, can't create unix socket file" % prefix)

    ss = UnixStreamServer(PluginServer(loglevel=Logger.WARNING - args.verbose), prefix)
    ss.ps.set_plugin_dir(args.directory)
    if args.dump_info:
        ret, err = ss.ps.get_plugin_info(args.dump_info)
        if err:
            raise Exception("error dump info: " + err)
        if PY3K:
            sys.stdout.buffer.write(msgpack.packb(ret))
        else:
            sys.stdout.write(msgpack.packb(ret))
        sys.exit(0)
    elif args.dump_all_info:
        plugins = ss.ps.get_available_plugins()
        ret = []
        for p in plugins:
            inf, err = ss.ps.get_plugin_info(p)
            if err:
                raise Exception("error dump info for " + p  + " : " + err)
            ret.append(inf)
        sys.stdout.write(json.dumps(ret))
        sys.exit(0)

    ss.serve_forever()
    