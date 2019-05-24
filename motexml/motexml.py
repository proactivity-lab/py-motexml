"""motexml.py: MoteXML."""
from __future__ import absolute_import

from codecs import decode, encode
import logging
import re
from xml.etree import ElementTree
from xml.dom import minidom

from motexml import mle

log = logging.getLogger(__name__)

__author__ = "Raido Pahtma"
__license__ = "MIT"


if hasattr(ElementTree, 'ParseError'):
    ETREE_EXCEPTIONS = (ElementTree.ParseError)
else:  # Python <= 2.6
    from xml.parsers import expat
    ETREE_EXCEPTIONS = (expat.ExpatError)


def xml_from_file(filename):
    try:
        with open(filename, 'r') as f:
            return ElementTree.fromstring(f.read())
    except IOError:
        log.exception("")
        return None


def xml_from_string(xmlstring):
    try:
        element = ElementTree.fromstring(xmlstring)
    except ETREE_EXCEPTIONS as e:
        log.error("xml_from_string exception: %s", e.msg)
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


def get_ovalue(element, key="value"):
    if element is not None:
        v = element.get(key)
        if v is not None:
            v = v.lstrip().rstrip()
            if v.startswith("0x") or v.startswith("0X"):
                return int(v, 16)
            if v.startswith("0b") or v.startswith("0B"):
                return int(v, 2)
            elif "." in v:
                return int(float(v))
            else:
                return int(v)

    return None


def get_svalue(element):
    if element is not None:
        v = element.get("value")
        if v is not None:
            return v.lstrip().rstrip()
    return None


def get_buffer_as_uint8_list(element):
    if element is not None:
        b = element.get("buffer")
        if b is not None:
            if len(b) > 0 and (len(b) % 2) == 0:
                return [int(b[i:i+2], 16) for i in range(0, len(b), 2)]
            else:
                log.error("bad buffer length %u : %s", len(b), b)

    return None


class MoteXMLTranslator(object):

    def __init__(self, filename = None):
        self._tagdbint = {}
        self._tagdbintrepr = {}
        self._tagdbstr = {}
        self._tagdbint[0] = "dt_none"
        self._tagdbstr["dt_none"] = 0
        if filename is not None:
            self.load_tag_db(filename)

    def load_tag_db(self, filename):
        with open(filename, 'r') as f:
            for lnum, line in enumerate(f):
                line = line.split("#")[0].rstrip().lstrip()
                if line:
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
                                    log.error("%s line %i: Cannot use \"%s\" as formatting string",
                                              filename, lnum, tokens[2])
                                    self._tagdbintrepr[code] = "%i"
                        else:
                            self._tagdbintrepr[code] = "%i"

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
                buf = decode(element.get("buffer"), "hex")
                mlobject.setBuffer(buf, len(buf))

            ndex = enc.appendObject(mlobject)

            for c in list(element):
                if self._append_with_children(enc, ndex, c) != 0:
                    return 1
        else:
            log.error("tag %s is unknown", element.tag)
            return 1
        return 0

    def translate_from_xml(self, xml_packet):
        enc = mle.MLE()
        for c in list(xml_packet):
            if self._append_with_children(enc, 0, c) != 0:
                return None
        return enc.str()

    def _xml_append_with_children(self, element, subject, mote_packet):
        iterator = mle.MLI(mote_packet)
        obj = iterator.nextWithSubject(subject)
        while obj is not None:
            if obj.type in self._tagdbint:
                type = self._tagdbint[obj.type]
                repr = self._tagdbintrepr[obj.type]
            else:
                type = "dt_unknown_%08x" % (obj.type & 0xffffffff)
                repr = "%i"
                log.warning("type %x is unknown", obj.type & 0xffffffff)

            subelement = ElementTree.SubElement(element, type)
            if obj.valueIsPresent:
                if repr == "dt_types":
                    if obj.value in self._tagdbint:
                        value = self._tagdbint[obj.value]
                    else:
                        value = "0x%X" % (obj.value)
                else:
                    value = repr % (obj.value)
                subelement.set("value", value)
            if obj.bufferLength > 0:
                subelement.set("buffer", encode(obj.getBuffer(), "hex"))

            if self._xml_append_with_children(subelement, obj.index, mote_packet) > 0:
                return 1

            obj = iterator.nextWithSubject(subject)

        return 0

    def translate_to_xml(self, mote_packet):
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

        log.info("%s%s %s %s", depth*"    ", element.tag, value, known)
        for c in list(element):
            if c != element:
                if c is not None:
                    self._printchildren(c, depth + 1)

    def printelement(self, element):
        self._printchildren(element, 0)
