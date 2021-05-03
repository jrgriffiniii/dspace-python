#!/bin/env python
import argparse
import os, os.path
import sys
import glob
import subprocess
import requests

URL = "https://dataspace.princeton.edu/jspui/handle/{}"
CMD = 'curl -s -o /dev/null -w "%{http_code}" '


parser = argparse.ArgumentParser(
    description="test arks in mapfile against dataspace.princeton.edu"
)
parser.add_argument("mapfiles", nargs="+", help="mapfilepattern ")
args = parser.parse_args()

for mapfile in args.mapfiles:
    for line in open(mapfile, "r"):
        [etd, ark] = line.strip().split(" ")
        url = URL.format(ark)
        r = requests.get(url)
        print(url, r)
