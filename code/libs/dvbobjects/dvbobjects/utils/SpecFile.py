#! /usr/bin/env python

#
# Copyright (C) 2000-2001, GMD, Sankt Augustin
# -- German National Research Center for Information Technology
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import string
from dvbobjects.utils import *

######################################################################


class SuperGroupSpec(DVBobject):

    def read(self, filename):
        self.PATH = filename
        with open(filename, 'r') as file:
            items = file.readline().strip().split()

            print ("SuperGroupSpec items:", items)
            self.transactionId = eval(items[0])
            self.version = eval(items[1])
            fn = items[1]
            if fn == "None":
                self.srg_ior = None
            else:
                with open(items[2], 'rb') as srg_file:
                    self.srg_ior = srg_file.read()


            self.groups = []

            print ("FFFFILE:", file)
            while (1):
                line = file.readline()
                if not line:
                    break

                group = GroupSpec()
                # print repr(line)
                group.read(line)
                self.groups.append(group)

    def write(self, outputDir):
        print ("specFile write:", self, outputDir)
        specFile = "%s/DSI.spec" % outputDir
        dsi = open(specFile, "wb")
        print ("DSI Print:" , dsi)

        initial_line = f"0x{self.transactionId.version:08X} 0x{self.version:08X} {self.srg_ior}\n"
        dsi.write(initial_line.encode('utf-8'))

        for group in self.groups:
            print ("Group write:" ,dsi, outputDir)
            group.write(dsi, outputDir)

    def addGroup(self, **kwargs):
        group = GroupSpec(*[], **kwargs)
        try:
            self.groups.append(group)
        except AttributeError:
            self.groups = [group]

    def addModule(self, **kwargs):
        curr = self.groups[-1]
        GroupSpec.addModule(*(curr,), **kwargs)

######################################################################


class GroupSpec(DVBobject):

    def read(self, specline):
        items = specline.split()

        self.PATH = items[0]
        # print repr(items[0])
        diiSpecFile = open(items[0])
        self.transactionId = eval(items[1])
        self.version = eval(items[2])
        self.downloadId = eval(items[3])
        if len(items) == 6:
            self.assocTag = eval(items[4])
            self.blockSize = eval(items[5])
        else:
            self.assocTag = None
            self.blockSize = eval(items[6])

        self.modules = []

        while 1:
            line = diiSpecFile.readline()
            if not line:
                break

            mod = ModuleSpec()
            mod.read(line)
            self.modules.append(mod)

    def write(self, specFile, outputDir):
        print(self.transactionId)

        print ("specFile write:" , "%s 0x%08X 0x%08X 0x%08X 0x%04X %4d\n" % (
                "%s/DII.spec" % outputDir,
                int(self.transactionId.identification),
                self.version,
                self.downloadId,
                self.assocTag,
                self.blockSize,
            ))
 
        specFile.write(
            ("%s 0x%08X 0x%08X 0x%08X 0x%04X %4d\n" % (
                "%s/DII.spec" % outputDir,
                int(self.transactionId.identification),
                self.version,
                self.downloadId,
                self.assocTag,
                self.blockSize,
            )).encode('utf-8'))

    def addModule(self, **kwargs):
        mod = ModuleSpec(*(), **kwargs)
        try:
            self.modules.append(mod)
        except AttributeError:
            self.modules = [mod]

######################################################################


class ModuleSpec(DVBobject):

    def read(self, specline):
        items = specline.split()
        # print repr(items[0])
        # print repr(items[1])
        self.INPUT = items[0]
        self.tableid = eval(items[1])
        self.moduleId = eval(items[2])
        self.moduleVersion = eval(items[3])

######################################################################
