# coding:utf-8
# Contributor:
#      fffonion        <fffonion@gmail.com>

import os
import re
import sys
import argparse
import traceback
import msgpack
import json

from .server import PluginServer
from .listener import UnixStreamServer, DEFAULT_SOCKET_NAME
from .logger import Logger

from .const import __version__, PY3K

def parse(dedicated=False):
    parser = argparse.ArgumentParser(description='Kong Python Plugin Server.')
    parser.add_argument('-p', '--kong-prefix', '-kong-prefix',
                        dest='prefix', metavar='prefix', type=str,
                        default="/usr/local/kong/",
                        help='Unix domain socket path to listen')
    parser.add_argument('-v', '--verbose', action='count', default=1,
                        help='Turn on verbose logging')
    parser.add_argument('--version', '-version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('--socket-name', type=str, dest='socket_name', default=DEFAULT_SOCKET_NAME,
                    help='socket name to listen on')
    mxg = parser.add_mutually_exclusive_group()
    mxg.add_argument('-m', '--multiprocessing', dest='multiprocessing', action="store_true",
                        help='Enable multiprocessing')
    mxg.add_argument('-g', '--gevent', dest='gevent', action="store_true",
                        help='Enable gevent')

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

    if not os.path.exists(args.prefix):
        raise OSError("path %s doesn't exist, can't create unix socket file" % args.prefix)

    return args

def start_server():
    args = parse()

    prefix = args.prefix

    ps = PluginServer(loglevel=Logger.WARNING - args.verbose,
                        plugin_dir=args.directory,
                        multiprocess=args.multiprocessing)
    ss = UnixStreamServer(ps, prefix,
                            sock_name=args.socket_name,
                            use_gevent=args.gevent)
    if args.dump_info:
        ret, err = ps.get_plugin_info(args.dump_info)
        if err:
            raise Exception("error dump info: " + err)
        if PY3K:
            sys.stdout.buffer.write(msgpack.packb(ret))
        else:
            sys.stdout.write(msgpack.packb(ret))
        sys.exit(0)
    elif args.dump_all_info:
        ret = []
        for p in ps.plugins:
            inf, err = ps.get_plugin_info(p)
            if err:
                raise Exception("error dump info for " + p  + " : " + err)
            ret.append(inf)
        sys.stdout.write(json.dumps(ret))
        sys.exit(0)

    try:
        ss.serve_forever()
    except KeyboardInterrupt:
        ps.logger.info("polite exit requested, terminating...")

    ps.cleanup()

def start_dedicated_server(name, plugin, _version=None, _priority=0):
    from .module import Module

    args = parse(dedicated=True)

    ps = PluginServer(loglevel=Logger.WARNING - args.verbose,
                        multiprocess=args.multiprocessing,
                        name="%s version %s" % (name, _version or 'unknown'))
    socket_name = args.socket_name
    if socket_name == DEFAULT_SOCKET_NAME:
        socket_name = "%s.sock" % name.replace("-", "_")
    ss = UnixStreamServer(ps, args.prefix,
                            sock_name=socket_name,
                            use_gevent=args.gevent)

    class mod(object):
        Plugin = plugin
        version = _version
        priority = _priority

    mod = Module(name, module=mod)
    ps.plugins[name] = mod

    if args.dump:
        ret, err = ps.get_plugin_info(name)
        if err:
            raise Exception("error dump info: " + err)
        # note a list is returned
        sys.stdout.write(json.dumps([ret]))
        sys.exit(0)

    try:
        ss.serve_forever()
    except KeyboardInterrupt:
        ps.logger.info("polite exit requested, terminating...")

    ps.cleanup()