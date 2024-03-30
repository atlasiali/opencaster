# This file is part of the dvbobjects library.
#
# Copyright 2000-2001, GMD, Sankt Augustin
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

import os
import string
import struct
from dvbobjects.utils import *
from dvbobjects.MHP.Descriptors import content_type_descriptor

######################################################################


class Message(DVBobject):

    magic = "BIOP"                      # ISO
    biop_version_major = 0x01           # ISO
    biop_version_minor = 0x00           # ISO
    byte_order = 0x00                   # DVB
    message_type = 0x00                 # ISO
    serviceContextList = ""             # MHP

    def pack(self):
        
        print ("Pack:",self)
        # sanity check
        assert self.byte_order == 0x00  # DVB
        assert len(self.objectKind) == 0x04, repr(self.objectKind)  # DVB
        print ("HHHHELLLLLO",self)
        print (type(self.objectKind), type(self.objectInfo), type(self.serviceContextList))
        print (self.objectKind, self.objectInfo, self.serviceContextList)

        if isinstance(self.objectKind, str):
             self.objectKind = self.objectKind.encode('utf-8')

        if isinstance(self.objectInfo, str):
             self.objectInfo = self.objectInfo.encode('utf-8')

        if isinstance(self.serviceContextList, str):
             self.serviceContextList = self.serviceContextList.encode('utf-8')

        if isinstance(self.magic, str):
             self.magic = self.magic.encode('utf-8')

        print (type(self.objectKind), type(self.objectInfo), type(self.serviceContextList))

        MessageSubHeader_FMT = (
            "!"
            "B"
            "L"                      # objectKey
            "L"
            "%ds"                      # objectKind
            "H"
            "%ds"                      # objectInfo
            "B"
            "%ds"                      # serviceContextList
        ) % (
            len(self.objectKind),
            len(self.objectInfo),
            len(self.serviceContextList),
        )
        print ("BELLLLLLO")
        MessageSubHeader = pack(
            MessageSubHeader_FMT,
            4,
            self.objectKey,
            len(self.objectKind),
            self.objectKind,
            len(self.objectInfo),
            self.objectInfo,
            len(self.serviceContextList),
            self.serviceContextList,
        )
        print ("Before messageBody")

        messageBody = self.messageBody()
        print ("pack messageBody:", messageBody)
        message_size = (
            len(MessageSubHeader)
            + 4                         # messageBody_length field
            + len(messageBody)
        )
        print ("pack messageSizeMMM:", message_size)

        print (type(self.magic), type(self.biop_version_major), type(self.biop_version_minor))
        print ("Chelllloooo")
        MessageHeader = pack(
            "!"
            "4s"                        # magic
            "B"                         # biop_version_major
            "B"                         # biop_version_minor
            "B"                         # byte_order
            "B"                         # message_type
            "L"                         # message_size
            ,                           # end of FMT ;-)
            self.magic,
            self.biop_version_major,
            self.biop_version_minor,
            self.byte_order,
            self.message_type,
            message_size,               # computed
        )

        print ("Message Header")
        FMT = ("!"
               "%ds"                    # MessageHeader
               "%ds"                    # MessageSubHeader
               "L"                      # messageBody_length
               "%ds"                    # messageBody
               ) % (
            len(MessageHeader),
            len(MessageSubHeader),
            len(messageBody)
        )

        print ("Returning pack")
        return pack(
            FMT,                        # see above
            MessageHeader,
            MessageSubHeader,
            len(messageBody),           # messageBody
            messageBody,
        )

######################################################################


class FileMessage(Message):

    objectKind = CDR("fil").encode('utf-8')             # DVB

    def __init__(self, **kwargs):
        print ("Hello from FileMessage")
        # Initialize SuperClass
        Message.__init__(*(self,), **kwargs)

        # Initialize standard attributes
        self.set(
            objectInfo=pack("!LL", 0, self.contentSize),
        )

        print ("Filemessage self:",self)
        # Maybe we're playing MHP...
        try:
            content_type = self.content_type
        except AttributeError:
            content_type = None         # i.e: UNKNOWN

        print ("Filemessage contenttype:",content_type)
        # if we know a content_type, add descriptor...
        if content_type:
            ctd = content_type_descriptor(content_type=content_type)
            self.objectInfo = self.objectInfo + ctd.pack()

    def messageBody(self):
        # Retrieve the file message body (i.e. file content)
        print ("Retrieve the file message body")
 
        with open(self.PATH, 'rb') as file:
            content = file.read()

        print ("file readed rb", content) 
        content_length = len(content)
        assert content_length == self.contentSize, self.PATH

        return pack("!L%ds" % content_length,
                    content_length,
                    content,
                    )

######################################################################


class StreamEventMessage(Message):

    objectKind = CDR("ste").encode('utf-8')             # DVB
    objectInfo = ""

    def __init__(self, **kwargs):
        print ("Stream Event")
        # Initialize SuperClass
        Message.__init__(*(self,), **kwargs)

        info_t = pack("!BLLBBB", 0, 0, 0, 0, 0, 1)
        # Hard coded DSM::Stream::Info_T.pack() for do it now
        event_names = open(self.PATH + "/.ename").read()
        self.objectInfo = info_t + event_names

    def messageBody(self):
        print ("Stream messagebody")
        # stream event do it now: BIOP.program_use_tap (id undefined) + eventIds
        taps = open(self.PATH + "/.tap").read()
        event_ids = open(self.PATH + "/.eid").read()
        return taps + event_ids


######################################################################
class DirectoryMessage(Message):

    objectKind = CDR("dir").encode('utf-8')             # DVB
    objectInfo = b""                     # MHP

    def __init__(self, **kwargs):

        # Initialize SuperClass
        super().__init__(**kwargs)
        self.bindings_count = len(self.bindings)

        assert self.bindings_count < 512  # MHP


    def messageBody(self):
        print ("Directory Message",self)

        bindings_bytes = b"".join(binding.pack() for binding in self.bindings)


        print ("LALALALLLL")
        FMT = "!H%ds" % len(bindings_bytes)

        print (type(FMT),type(len(self.bindings)),type(bindings_bytes))
        messageBody = pack(
            FMT,
            len(self.bindings),
            bindings_bytes,
        )

        print ("Dir msg:", messageBody)
        return messageBody

######################################################################


class ServiceGatewayMessage(DirectoryMessage):
    print ("ServiceGatewayMessage")
    objectKind = CDR("srg").encode('utf-8')             # DVB

######################################################################


class ServiceGatewayInfo(DVBobject):

    print ("ServiceGatewayInfo", DVBobject)
    userInfo = b""                       # MHP

    def pack(self):
        print ("ServiceGatewayInfo PPACK:",self)
        FMT = ("!"
               "%ds"                    # IOP::IOR
               "B"                      # downloadTaps_count
               "B"                      # serviceContextList_count
               "H%ds"                   # userInfo
               ) % (
            len(self.srg_ior),
            len(self.userInfo),
        )

        return pack(FMT,
                    self.srg_ior,       # IOP::IOR
                    0,                  # downloadTaps_count
                    0,                  # serviceContextList_count
                    len(self.userInfo),
                    self.userInfo,
                    )
