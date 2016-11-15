#! /usr/bin/env python3
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

import networkx as nx
import os
import signal
import sys

from server import Server
from app.riot_native import RIOTNativeApp
from node import Node
import config

import matplotlib.pyplot as plt

apps = []
zep_server = None

def signal_handler(signal, frame):
    global apps
    for app in apps:
        del app
        app = None
    apps = []
    sys.exit(0)

def main():
    global apps, zep_server
    mesh, args = config.load()

    if not args.input_file:
        template = mesh
        mesh = nx.Graph()
        signal.signal(signal.SIGINT, signal_handler)
        for n in template.nodes():
            app = RIOTNativeApp(os.path.join(os.environ['RIOTBASE'],
                "examples/gnrc_networking/bin/native/gnrc_networking.elf"),
                "gnrc_networking")
            node = Node("::1", app.zep_port, app)
            mesh.add_node(node)
            apps.append(app)
        for e in template.edges():
            edge = (mesh.nodes()[e[0]], mesh.nodes()[e[1]])
            mesh.add_edge(*edge)

    zep_server = Server(mesh=mesh, dump=args.dump_pcap)
    with zep_server.mesh_lock:
        config.store_mesh("mesh.json", zep_server.mesh)
    labels = {}
    for node in mesh.nodes():
        labels[node] = 'localhost:%u\n%s' % (node.application.terminal_port,
                                             node.application.link_local_addr)
    pos = nx.spring_layout(mesh)
    n = nx.draw_networkx_nodes(mesh, pos, labels=labels, font_size=10, node_color='w', node_size=100)
    n.set_edgecolor('gray')
    n = nx.draw_networkx_edges(mesh, pos, labels=labels, font_size=10, node_color='w', node_size=100)
    n.set_edgecolor('gray')
    nx.draw_networkx_labels(mesh, pos, labels=labels, font_size=10, node_color='w', node_size=100)
    plt.show()
    zep_server.join()

if __name__ == "__main__":
    main()
