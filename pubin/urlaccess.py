#!/usr/bin/env python
import argparse
import sys

def main():
    description = """peal date and accessor out of DSpace's apache log"""
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--url', '-u', default='robots.txt', help='look for urls containing given string')
    parser.add_argument('--log', '-l', default='/var/log/httpd/access_log', help='appache log file')
    args = parser.parse_args()

    print("# %s accesses found in %s" % (args.url, args.log))
    try:
        for line in  open(args.log, "r"):
            if (args.url in line):
                line = line.strip()
                parts = line.split('-', 2)
                if (len(parts) == 3):
                    ip = parts[0]
                    rests = parts[2].strip(' ').split('"')
                    datestr = rests[0].rstrip(']').lstrip('[')
                    date = datestr.split(' ')[0]
                    accesor = rests[-2]
                    urli = accesor.rfind("://")
                    if (-1 < urli):
                        print("\t".join([date, accesor[urli+3:-1]]))

    except Exception as e:
        print("must give valid log file\n" + str(e))

if __name__ == "__main__":
    main()
