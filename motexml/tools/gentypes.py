#!/usr/bin/env python
"""gentypes.py: MoteXML header generator."""
import re
import time
import getpass

__author__ = "Raido Pahtma"
__license__ = "MIT"


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
                        except Exception:
                            print("Error: Unable to parse line %u: \"%s\"" % (l, iline))
                            print(split)
                            return None

                        db.append((code, name, comment))

                # Name is made up of multiple words, first one will be used
                if len(split) > 3:
                    print("Warning: Line %u not formatted correctly: \"%s\"" % (l, iline))

    return db


def write_output(dt_types, filename):
    try:
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
    except Exception:
        pass

    return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="dt_types.h generator",
                                     epilog="Input file format: \"XX,name # comment\" (\"FF,dt_end # The end of something\")",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--input", default="dt_types.txt", help="dt_types input file")
    parser.add_argument("--output", default="dt_types.h", help="dt_types output file")

    args = parser.parse_args()

    dt_types = read_input(args.input)

    if dt_types is not None:
        print("Read %u types from %s" % (len(dt_types), args.input))

        if write_output(dt_types, args.output):
            print("Created %s" % (args.output))
        else:
            print("Failed to create %s" % (args.output))
    else:
        print("Unable to process %s" % (args.input))


if __name__ == '__main__':
    main()
