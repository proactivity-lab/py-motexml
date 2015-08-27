#
# Copyright (c) 2011 Tallinn University of Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the
#   distribution.
# - Neither the name of the copyright holders nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
# @author Raido Pahtma
#
import re
import mle
from xml.etree import ElementTree
from xml.dom import minidom

if hasattr(ElementTree, 'ParseError'):
    ETREE_EXCEPTIONS = (ElementTree.ParseError)
else: # Python <= 2.6
    from xml.parsers import expat
    ETREE_EXCEPTIONS = (expat.ExpatError)

import logging
log = logging.getLogger(__name__)

def xml_from_file(filename):
    try:
        with open(filename, 'r') as f:
            return ElementTree.fromstring(f.read())
    except:
        log.exception("")
        return None

def xml_from_string(xmlstring):
    try:
        element = ElementTree.fromstring(xmlstring)
    except ETREE_EXCEPTIONS as e:
        log.error("xml_from_string exception: %s" % e.msg)
        element = None

    return element

def xml_to_string(element):
    if element is not None:
        simple = ElementTree.tostring(element, 'utf-8')
        parsed = minidom.parseString(simple)
        pretty = parsed.toprettyxml(indent="    ")
        return "\n".join([ll.rstrip() for ll in pretty.splitlines() if ll.strip()])

    return "<dt_none/>"

def unsigned32(value):
    return 0xFFFFFFFF & value

def get_child_ovalue(element, child):
    if element is not None:
        ch = element.find(child)
        if ch is not None:
            return get_ovalue(ch)
    return None

def get_ovalue(element):
    if element is not None:
        v = element.get("value")
        if v is not None:
            v = v.lstrip().rstrip()
            if v.startswith("0x") or v.startswith("0X"):
                return int(v, 16)
            elif "." in v:
                return int(float(v))
            else:
                return int(v)

    return None


def get_buffer_as_uint8_list(element):
    if element is not None:
        b = element.get("buffer")
        if b is not None:
            if (len(b) > 0) and ((len(b) % 2) == 0):
                return [int(b[i:i+2], 16) for i in xrange(0, len(b), 2)]
            else:
                log.error("bad buffer length %u : %s" % (len(b), b))

    return None

class MoteXMLTranslator():

    def __init__(self, filename = None):
        self._tagdbint = {}
        self._tagdbintrepr = {}
        self._tagdbstr = {}
        self._tagdbint[0] = "dt_none"
        self._tagdbstr["dt_none"] = 0
        if filename is not None:
            self.load_tag_db(filename)

    def load_tag_db(self, filename):
        f = open(filename, 'r')
        lnum = 0
        for line in f:
            lnum += 1
            line = line.split("#")[0].rstrip().lstrip()
            if len(line) > 0:
                tokens = re.findall(r'[\w|%]+', line)
                if len(tokens) >= 2:
                    code = int(tokens[0], 16)
                    text = tokens[1]
                    self._tagdbint[code] = text
                    self._tagdbstr[text] = code
                    if len(tokens) >= 3:
                        if tokens[2] == "dt_types":
                            self._tagdbintrepr[code] = tokens[2]
                        else:
                            try:
                                tokens[2] % (0)
                                self._tagdbintrepr[code] = tokens[2]
                            except TypeError:
                                log.error("%s line %i: Cannot use \"%s\" as formatting string" % (filename, lnum, tokens[2]))
                                self._tagdbintrepr[code] = "%i"
                    else:
                        self._tagdbintrepr[code] = "%i"

        f.close()

    def _get_string_value(self, element):
        """
        Assume that the element value is another tag type and try to look it up.
        """
        if element is not None:
            v = element.get("value")
            if v is not None:
                v = v.lstrip().rstrip()
                if v in self._tagdbstr:
                    return self._tagdbstr[v]
                raise ValueError("%s" % v)
        return None

    def _append_with_children(self, enc, subject, element):
        if element.tag in self._tagdbstr:
            mlobject = mle.MLObject()
            mlobject.type = self._tagdbstr[element.tag]
            mlobject.subject = subject

            try:
                value = get_ovalue(element)
                if value is not None:
                    mlobject.setValue(value)
            except ValueError:  # Has value, but not a number, maybe it is a string that can be turned into a number
                try:
                    value = self._get_string_value(element)
                    if value is not None:
                        mlobject.setValue(value)
                except ValueError:
                    log.exception("")
                    return 1

            if element.get("buffer") is not None:
                buf = element.get("buffer").decode("hex")
                mlobject.setBuffer(buf, len(buf))

            ndex = enc.appendObject(mlobject)

            for c in list(element):
                if self._append_with_children(enc, ndex, c) != 0:
                    return 1
        else:
            log.error("tag %s is unknown" % (element.tag))
            return 1
        return 0

    def translate_from_xml(self, xml_packet):
        enc = mle.MLE()
        for c in list(xml_packet):
            if self._append_with_children(enc, 0, c) != 0:
                return None
        return enc.str()

    def _xml_append_with_children(self, element, subject, mote_packet):
        iter = mle.MLI(mote_packet)
        object = iter.nextWithSubject(subject)
        while object is not None:
            if object.type in self._tagdbint:
                type = self._tagdbint[object.type]
                repr = self._tagdbintrepr[object.type]
            else:
                type = "dt_unknown_%08x" % (object.type & 0xffffffff)
                repr = "%i"
                log.warning("type %x is unknown" % (object.type & 0xffffffff))

            subelement = ElementTree.SubElement(element, type)
            if object.valueIsPresent:
                if repr == "dt_types":
                    if object.value in self._tagdbint:
                        value = self._tagdbint[object.value]
                    else:
                        value = "0x%X" % (object.value)
                else:
                    value = repr % (object.value)
                subelement.set("value", value)
            if object.bufferLength > 0:
                subelement.set("buffer", object.getBuffer().encode("hex"))

            if self._xml_append_with_children(subelement, object.index, mote_packet) > 0:
                return 1

            object = iter.nextWithSubject(subject)

        return 0

    def translate_to_xml(self, mote_packet):
        iter = mle.MLI(mote_packet)
        element = ElementTree.Element("xml_packet")
        if self._xml_append_with_children(element, 0, mote_packet) == 0:
            return element

        return None

    def _printchildren(self, element, depth):
        known = ""
        value = ""
        if element.tag not in self._tagdbstr:
            known = "(UNKNOWN TAG)"

        if element.get("value") is not None:
            value = "value=" + str(element.get("value"))

        log.info("%s%s %s %s" % (depth*"    ", element.tag, value, known))
        for c in list(element):
            if c != element:
                if c is not None:
                    self._printchildren(c, depth + 1)

    def printelement(self, element):
        self._printchildren(element, 0)
