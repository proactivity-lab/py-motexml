#! /usr/bin/env python
#
# Copyright (c) 2012 Tallinn University of Technology
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
import re
import time
import getpass

def read_input(filename):
    f = open(filename, "r")
    l = 0
    db = []
    for iline in f:
        l += 1
        line = iline = iline.lstrip().rstrip()
        if len(line) > 0:

            # Deal with comments
            split = line.split("#", 1)
            if len(split) > 1 and len(split[0]) > 0 and len(split[1]) > 0:
                line = split[0].rstrip()
                comment = split[1].lstrip().rstrip()
            else:
                line = split[0].rstrip()
                comment = None

            if len(line) > 0:
                # Split the line into code and name
                split = re.findall(r'[\w|%]+', line)
                if len(split) >= 2:
                    code = split[0]
                    name = split[1]

                    if name != "-":
                        try:
                            code = int(code, 16)
                        except:
                            print "Error: Unable to parse line %u: \"%s\"" % (l, iline)
                            print split
                            return None

                        db.append((code, name, comment))

                # Name is made up of multiple words, first one will be used
                if len(split) > 3:
                    print "Warning: Line %u not formatted correctly: \"%s\"" % (l, iline)

    return db

def write_output(dt_types, filename):
    with open(filename, "w") as f:
        f.write("""/**\n""")
        f.write(""" * Automatically generated dt_types.h\n""")
        f.write(""" *\n""")
        f.write(""" * @brief dt_types enums\n""")
        f.write(""" * @author %s\n""" % (getpass.getuser()))
        f.write(""" * @date %s\n""" % (time.strftime("%Y-%m-%d %X", time.localtime())))
        f.write(""" */\n""")
        f.write("""#ifndef DT_TYPES_H_\n""")
        f.write("""#define DT_TYPES_H_\n""")
        f.write("""\n""")
        f.write("""enum dt_types {\n""")

        for d in dt_types:
            f.write("""\t%s = 0x%X,""" % (d[1], d[0]))
            if d[2] is not None:
                f.write(""" // %s""" % (d[2]))
            f.write("""\n""")

        f.write("""};\n""")
        f.write("""\n""")
        f.write("""#endif /* DT_TYPES_H_ */""")
        f.write("""\n""")

        return True

    return False

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="dt_types.h generator",
                                     epilog="Input file format: \"XX,name # comment\" (\"FF,dt_end # The end of something\")",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--input", default="dt_types.txt", help="dt_types input file")
    parser.add_argument("--output", default="dt_types.h", help="dt_types output file")

    args = parser.parse_args()

    dt_types = read_input(args.input)

    if dt_types is not None:
        print "Read %u types from %s" % (len(dt_types), args.input)

        if write_output(dt_types, args.output) == True:
            print "Created %s" % (args.output)
        else:
            print "Failed to create %s" % (args.output)
    else:
        print "Unable to process %s" % (args.input)


