#!/usr/bin/env python
"""mlhextoxml.py: MoteXML binary to XML translator."""
from motexml import motexml

__author__ = "Raido Pahtma"
__license__ = "MIT"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="print hex as XML")
    parser.add_argument("hexdata", default=None, nargs="+", help="Input data")
    parser.add_argument("--types", default="../../dt_types.txt", help="dt_types text file")
    args = parser.parse_args()

    hexdata = "".join(args.hexdata)

    print("Hex length = %u" % (len(hexdata) / 2))
    print(hexdata)

    data = hexdata.decode("hex")

    # Generate C compatible initializer array
    out_arr = ""
    for i in range(0, len(data)):
        out_arr += "0x%x," % (ord(data[i]))
    print("{%s}" % out_arr[:-1])

    # Translate to XML
    trans = motexml.MoteXMLTranslator(args.types)
    xdata = trans.translate_to_xml(data)
    print("")
    if xdata is not None:
        print(motexml.xml_to_string(xdata))
    else:
        print("ERROR: XML translation failed")


if __name__ == '__main__':
    main()
