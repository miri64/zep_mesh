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

import sys
import struct
import time

MAGIC = 0xa1b2c3d4
MAJOR = 2
MINOR = 4
ZONE = 0
SIG = 0
SNAPLEN = 0xffff
NETWORK = 195       # 802.15.4 with FCS

class PCAPWriterStdout(object):
    def start(self):
        sys.stdout.buffer.write(struct.pack('<LHHLLLL', MAGIC, MAJOR, MINOR,
                                            ZONE, SIG, SNAPLEN, NETWORK))

    def dump(self, t, pkt):
        sec = int(time.mktime(t.timetuple()))
        usec = t.microsecond
        sys.stdout.buffer.write(struct.pack('<LLLL', sec, usec, len(pkt),
                                            len(pkt)))
        sys.stdout.flush()
        for byte in pkt:
            sys.stdout.buffer.write(struct.pack('<B', byte))
        sys.stdout.flush()
