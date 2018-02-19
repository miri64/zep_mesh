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

class Node(object):
    def __init__(self, sock_addr, sock_port, application = None):
        self.sock_addr = sock_addr
        self.sock_port = sock_port
        self.application = application

    def __eq__(self, other):
        return (self.sock_addr == other.sock_addr) and \
               (self.sock_port == other.sock_port)

    def __hash__(self):
        return hash((self.sock_addr, self.sock_port))

    def to_json(self):
        d = { "sock_addr": [ self.sock_addr, self.sock_port ] }
        if self.application != None:
            d["application"] = self.application.to_json()
        return d

    def to_sockaddr(self):
        return (self.sock_addr, self.sock_port)

