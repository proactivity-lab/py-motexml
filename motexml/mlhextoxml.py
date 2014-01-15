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
import argparse

import motexml
import mle

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="print hex as XML")
    parser.add_argument("hexdata", default=None, help="Input data")
    parser.add_argument("--types", default="../../dt_types.txt", help="dt_types text file")
    parser.add_argument("--log", action="store_true")
    args = parser.parse_args()

    if args.log == True:
        import logging_setup.logging_setup as logging_setup
        logging_setup.setup("mlhextoxml", "log")

    print "Hex length = %u" % (len(args.hexdata) / 2)
    print args.hexdata

    data = args.hexdata.decode("hex")

    # Generate C compatible initializer array
    outputarray = ""
    for i in range(0, len(data)):
        outputarray += "0x%x," % (ord(data[i]))
    print "{%s}" % outputarray[:-1]

    # Translate to XML
    trans = motexml.MoteXMLTranslator(args.types)
    xdata = trans.translate_to_xml(data)
    print ""
    if xdata is not None:
        print motexml.xml_to_string(xdata)
    else:
        print "ERROR: XML translation failed"
