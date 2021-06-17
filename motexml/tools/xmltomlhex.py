#!/usr/bin/env python
"""xmltomlhex.py: XML to MoteXML binary translator."""
from __future__ import print_function

from codecs import encode

from motexml import motexml

import os
from datetime import datetime

__author__ = "Raido Pahtma"
__license__ = "MIT"


header_template ="""\
/**
 * Header generated from "{input:}" on {timestamp:}.
 */
#ifndef {guard:}_
#define {guard:}_

uint8_t {array:}[] = {{{data:}}};

#endif//{guard:}_
"""


def main():
    import argparse
    parser = argparse.ArgumentParser(description="print hex as XML")
    parser.add_argument("filename", default=None, help="Input file name")
    parser.add_argument("--types", default="/usr/share/mist-dt-types/dt_types.txt", help="dt_types text file")
    parser.add_argument("--header", default=None, help="Generate a C header file with the data")
    parser.add_argument("--array", default="data", help="Name of the array in the C header file")
    args = parser.parse_args()

    trans = motexml.MoteXMLTranslator(args.types)

    xd = motexml.xml_from_file(args.filename)
    data = trans.translate_from_xml(xd)
    xd = trans.translate_to_xml(data)

    # Generate C compatible initializer array
    out_arr = ""
    for i in range(0, len(data)):
        out_arr += "0x%x," % (ord(data[i:i+1]))
    out_arr = out_arr[:-1]

    if args.header is not None:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
        hname = os.path.basename(args.header).replace(".", "_").upper()
        with open(args.header, 'wb') as f:
            f.write(header_template.format(input=os.path.basename(args.filename),
                                           timestamp=now,
                                           guard=hname,
                                           array=args.array,
                                           data=out_arr).encode('ascii'))
        print("Generated C header {} from {}".format(args.header, args.filename))
    else:
        print(motexml.xml_to_string(xd))
        print()

        hexdata = encode(data, "hex").decode("ascii")
        print("Hex length = {:d}".format(len(hexdata) // 2))
        print(hexdata)
        print()

        print("{{{}}}".format(out_arr))
        print()


if __name__ == '__main__':
    main()
