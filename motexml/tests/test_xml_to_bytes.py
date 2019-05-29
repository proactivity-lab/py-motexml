"""Test XML to bytes conversions."""
from codecs import decode
import os
from unittest import TestCase
from xml.etree import ElementTree

from motexml.motexml import MoteXMLTranslator

__author__ = "Kaarel Ratas"
__license__ = "MIT"


class XMLToBytesTester(TestCase):
    """Test XML input to binary output."""
    def setUp(self):
        # TODO: package dt_types.txt with this package somehow
        self.translator = MoteXMLTranslator(os.environ['DT_TYPES'])

    def test_packet_1(self):
        """Tests 1st sample packet."""
        etree = ElementTree.fromstring("""<?xml version="1.0" ?>
            <xml_packet>
                <dt_data>
                    <dt_data value="dt_external_temperature_C">
                        <dt_value value="-27315">
                            <dt_exp value="-2"/>
                        </dt_value>
                    </dt_data>
                    <dt_data value="dt_battery_V">
                        <dt_value value="3407">
                            <dt_exp value="-3"/>
                        </dt_value>
                    </dt_data>
                    <dt_age_ms value="10"/>
                </dt_data>
                <dt_subscription value="2">
                    <dt_provider buffer="0000000000000000"/>
                    <dt_seq value="8572"/>
                    <dt_resource buffer="f063c751a8d44673af386df82a9bb942"/>
                </dt_subscription>
            </xml_packet>
        """)
        result = self.translator.translate_from_xml(etree)
        expected = decode(b'080F4A010FE2004A02044D9549036EFE49010F364A05044F0D49066EFD'
                          b'4901590A090502C809D20800000000000000004A09087C21C8092210F0'
                          b'63C751A8D44673AF386DF82A9BB942', 'hex')
        self.assertEqual(result, expected)

    def test_packet_2(self):
        """Tests 2nd sample packet."""
        etree = ElementTree.fromstring("""<?xml version="1.0" ?>
            <xml_packet>
                <dt_data>
                    <dt_data value="dt_external_temperature_C">
                        <dt_value value="-27315">
                            <dt_exp value="-2"/>
                        </dt_value>
                    </dt_data>
                    <dt_data value="dt_battery_V">
                        <dt_value value="3407">
                            <dt_exp value="-3"/>
                        </dt_value>
                    </dt_data>
                    <dt_age_ms value="10"/>
                </dt_data>
                <dt_subscription value="2">
                    <dt_provider buffer="0000000000000000"/>
                    <dt_seq value="8571"/>
                    <dt_resource buffer="f063c751a8d44673af386df82a9bb942"/>
                </dt_subscription>
            </xml_packet>
        """)
        result = self.translator.translate_from_xml(etree)
        expected = decode(b'080F4A010FE2004A02044D9549036EFE49010F364A05044F0D49066EFD4'
                          b'901590A090502C809D20800000000000000004A09087B21C8092210F063'
                          b'C751A8D44673AF386DF82A9BB942', 'hex')
        self.assertEqual(result, expected)
