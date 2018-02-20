#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (C) 2016 Freie Universität Berlin
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

__author__      = "Martine Lenders"
__copyright__   = "Copyright (C) 2016 Freie Universität Berlin"
__license__     = "LGPLv2.1"
__email__       = "m.lenders@fu-berlin.de"

import os
import pexpect
import socket
import subprocess
import sys
import time

from .base import BaseApplication

reserved_ports = {}

def get_free_port(start_port=4711, max_range=1000, family=socket.AF_INET,
                  type=socket.SOCK_STREAM):
    for port in range(start_port, start_port + max_range):
        if (port not in reserved_ports.get((family, type), [])):
            try:
                s = socket.socket(family=family, type=type)
                s.bind(('', port))
                s.close()
                if (family, type) in reserved_ports:
                    reserved_ports[(family, type)].append(port)
                else:
                    reserved_ports[(family, type)] = [port]
                return port
            except socket.error as oe:
                if (oe.errno == 98):
                    continue
                else:
                    sys.exit(1)

class RIOTNativeApp(BaseApplication):
    def __init__(self, filename, name, terminal_port = None, zep_port = None,
                 tap = None, *args, **kwargs):
        super(RIOTNativeApp, self).__init__(filename, *args, **kwargs)
        self.pid = None
        self.name = name
        self.link_local_addr = None
        self.tap = tap
        if terminal_port:
            self.terminal_port = int(terminal_port)
        else:
            self.terminal_port = get_free_port()
        if zep_port:
            self.zep_port = int(zep_port)
        else:
            self.zep_port = get_free_port(family=socket.AF_INET6,
                                          type=socket.SOCK_DGRAM)

    def __del__(self):
        if self.pid:
            command = 'kill -9 %u' % (self.pid)
            subprocess.call(command, stderr=subprocess.PIPE, shell=True)
            self.pid = None

    def __str__(self):
        return self.name

    def start(self, args=[]):
        command = "socat EXEC:'%s %s -z [::1]\:%u\,[::1]\:17754 ',end-close,stderr,pty TCP-L:%u,reuseaddr,fork" \
                    % (self.filename, self.tap if self.tap else "", self.zep_port, self.terminal_port)
        try:
            p = subprocess.Popen(command, shell=True)
            self.pid = p.pid
            print("Started node at localhost:%u" % self.terminal_port, file=sys.stderr)
            match = self.input("ifconfig",
                    "inet6 addr: (fe80:[0-9a-f:]+)  scope: local")
            if match:
                self.link_local_addr = match.group(1).decode()
        except subprocess.CalledProcessError:
            sys.exit(1)

    def input(self, inp, exp_outp):
        child = pexpect.spawn("nc localhost %u" % self.terminal_port, timeout=1)
        child.expect("All up, running the shell now")
        child.sendline(inp)
        child.expect(exp_outp)
        match = child.match
        child.terminate(force=True)
        return match

    def to_json(self):
        d = { 'class': type(self).__module__ + '.' + type(self).__name__,
              'filename': self.filename, 'name': self.name,
              'zep_port': self.zep_port }

        if self.link_local_addr:
            d['link_local_addr'] = self.link_local_addr

        return d
