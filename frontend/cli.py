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

from .base import Frontend

class CLI(Frontend):
    def ask_y_n(self, question):
        reply = input("%s [Y/n]" % question).lower().strip()
        if (reply == "") or (reply[0] == "y"):
            return True
        else:
            return False

    def ask_list(self, question, check_conv):
        print("%s (Finish with double [ENTER])" % question)
        i = 0
        list = []
        reply = None
        while reply != "":
            reply = input("[%u]: " % i)
            try:
                if (reply != ""):
                    list.append(check_conv(reply))
                    i += 1
            except Exception as e:
                print(e)
        return list

    def ask_str(self, question):
        reply = input("%s " % question)
        return reply

