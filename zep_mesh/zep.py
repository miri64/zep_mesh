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

import datetime
import struct
import time

NTP_DELTA = 2208988800
ZEP_HDR_SIZE = 32

def ntp_to_system_time(date):
    """convert a NTP time to system time"""
    return date - NTP_DELTA

def system_to_ntp_time(date):
    """convert a system time to a NTP time"""
    return date + NTP_DELTA

def parse(buf):
    if len(buf) < ZEP_HDR_SIZE:
        return None
    data = struct.unpack(">2sBBBHBBLLL10pB", buf[:ZEP_HDR_SIZE])
    return datetime.datetime.utcfromtimestamp((data[7] - NTP_DELTA) + \
           (data[8] / 1000000000)), buf[ZEP_HDR_SIZE:]
