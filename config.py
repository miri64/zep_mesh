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

import argparse
import json
import networkx as nx
from networkx.readwrite import json_graph
import sys

import app
from node import Node

def _default_json_dumper(obj):
    return getattr(obj.__class__, "to_json", json.JSONEncoder().default)(obj)

def store_mesh(filename, mesh):
    json.dump(json_graph.node_link_data(mesh), open(filename, 'w'),
              default=_default_json_dumper)

def load_mesh(filename):
    mesh_dict = json.load(open(filename))
    nodes = []
    for node in mesh_dict['nodes']:
        n_obj = {}
        n_app = None
        if ('application' in node['id']):
            n_app = eval(node['id']['application']['class'])(**(node['id']['application']))
        n_obj['id'] = Node(application=n_app, *node['id']['sock_addr'])
        nodes.append(n_obj)
    mesh_dict['nodes'] = nodes
    return json_graph.node_link_graph(mesh_dict)

def load():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--dump-pcap", help="Dumps pcap of traffic to stdout", action="store_true")
    parser.add_argument("-i", "--input-file", help="JSON input file")
    parser.add_argument("-n", "--number",
                        help="Number of nodes to generate (if no input file is given)",
                        type=int, default=5)
    parser.add_argument("-c", "--connectedness",
                        help="Connectedness [0.2, 1.0) of the network (if now input file is given)",
                        type=float, default=0.75)
    args = parser.parse_args()
    if (args.input_file):
        mesh = load_mesh(args.input_file)
    else:
        mesh = nx.connected_watts_strogatz_graph(args.number,
                int(args.number * args.connectedness), args.connectedness)
    return mesh, args
