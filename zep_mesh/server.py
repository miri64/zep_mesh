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

import select
import socket
import time
import threading
import networkx as nx

from .frontend import cli
from .node import Node
from .pcap import PCAPWriter, PCAPWriterStdout
from .zep import parse as parse_zep

server_instance = None

def to_port_int(port_string):
    err_str = "Please use only dec or hex values in range [0, %u]" % 0xffff
    try:
        port = int(port_string)
    except ValueError:
        try:
            port = int(port_string, base=16)
        except ValueError:
            try:
                if (port_string[:2] != "0x"):
                    raise ValueError(err_str)
                port = int(port_string[2:], base=16)
            except ValueError:
                raise ValueError(err_str)
    if (port < 0) or (port > 0xffff):
        raise ValueError(err_str)
    return port

class Server(threading.Thread):
    TERMINATION_STRING = b"!!!TERMINATE!!!"

    def __new__(cls, *args, **kwargs):
        global server_instance
        if server_instance == None:
            server_instance = threading.Thread.__new__(cls)
        return server_instance

    def __init__(self, frontend=cli.CLI(), port=17754, mesh=None, dump=False,
                 dump_file=None):
        super(Server, self).__init__()
        self.port = port
        self.socket = socket.socket(family=socket.AF_INET6, type=socket.SOCK_DGRAM)
        self.socket.bind(('', self.port))
        self.frontend = frontend
        self.dump = dump or (type(dump_file) is str)
        self.dump_file = dump_file
        time.sleep(0.1)
        if mesh != None:
            self.mesh = mesh
        else:
            self.mesh = nx.Graph()
        self.mesh_lock = threading.RLock()
        self.start()

    def __del__(self):
        self.stop()

    def stop(self):
        s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_DGRAM)
        # send magic string
        s.sendto(Server.TERMINATION_STRING, ("::1", self.port))

    def __add_to_mesh_if_new(self, new):
        if new not in self.mesh:
            if self.frontend.ask_y_n("Shall [%s]:%u join the mesh?" %
                                     new.to_sockaddr()):
                self.mesh.add_node(new)
                if (len(self.mesh.nodes()) > 1):
                    neighbors = self.frontend.ask_list("What neighbors shall [%s]:%u have?" %
                                                       new.to_sockaddr(), to_port_int)
                    for neighbor in neighbors:
                        neigh = Node("::1", neighbor)
                        if neigh in self.mesh:
                            self.mesh.add_edge(new, neigh)

    def run(self):
        inputs = [self.socket]
        outputs = []
        with self.mesh_lock:
            for n in self.mesh.nodes():
                n.application.start(self.port)
        pcap = None
        if self.dump:
            if self.dump_file is None:
                pcap = PCAPWriterStdout()
            else:
                pcap = PCAPWriter(self.dump_file)
            pcap.start()
        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs,
                                                            inputs)
            for s in readable:
                if s is self.socket:
                    data, sender = s.recvfrom(180)
                    if data:
                        if data == Server.TERMINATION_STRING:
                            # terminate server
                            s.close()
                            return
                        # TODO: set LQI according to edge weight and check channel
                        if self.dump:
                            time, buf = parse_zep(data)
                            pcap.dump(time, buf)
                        with self.mesh_lock:
                            new = Node(*sender[:2])
                            self.__add_to_mesh_if_new(new)
                            for neighbor in self.mesh.neighbors(new):
                                s.sendto(data, neighbor.to_sockaddr())
