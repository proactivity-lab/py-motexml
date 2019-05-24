#!/usr/bin/env python
"""xmltomlhex.py: XML to MoteXML binary translator."""
from codecs import encode

from motexml import motexml

__author__ = "Raido Pahtma"
__license__ = "MIT"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="print hex as XML")
    parser.add_argument("filename", default=None, help="Input file name")
    parser.add_argument("--types", default="dt_types.txt", help="dt_types text file")
    args = parser.parse_args()

    trans = motexml.MoteXMLTranslator(args.types)

    xd = motexml.xml_from_file(args.filename)
    data = trans.translate_from_xml(xd)
    xd = trans.translate_to_xml(data)

    print(motexml.xml_to_string(xd))
    print("Hex length = %u" % (len(encode(data, "hex")) / 2))
    print(encode(data, "hex"))

    # Generate C compatible initializer array
    out_arr = ""
    for i in range(0, len(data)):
        out_arr += "0x%x," % (ord(data[i:i+1]))
    print("{%s}" % out_arr[:-1])


if __name__ == '__main__':
    main()
