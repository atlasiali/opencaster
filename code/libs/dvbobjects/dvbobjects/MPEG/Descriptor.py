#! /usr/bin/env python

# This file is part of the dvbobjects library.
#
# Copyright  2000-2001, GMD, Sankt Augustin
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

from dvbobjects.utils import *

######################################################################


class Descriptor(DVBobject):
    """The base class for all Descriptors.
    Subclasses must implement a bytes() method,
    that returns the descriptor body bytes.
    """

    def pack(self):
        bytes = self.bytes()
        return pack("!BB%ds" % len(bytes),
                    self.descriptor_tag,
                    len(bytes),
                    bytes,
                    )
