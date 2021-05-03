#! /usr/bin/env python
from __future__ import print_function

import argparse
from datetime import datetime
import os
import sys
import tempfile
import random

__RUN_ID__ = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
__REPORT_PATH__ = "www/reports/metadata"
__DSPACE_HOME__ = None  # set in main()


def main(csv_file, collection, solr):
    global __DSPACE_HOME__
    __DSPACE_HOME__ = env("DSPACE_HOME")

    check_collection_in_csv(csv_file, collection)
    export_metadata(collection)
    import_metadata(csv_file, collection)
    if solr:
        index_optimize()


def check_collection_in_csv(csv_file, collection):
    # just assume collection handle is in second column
    # in header line we get 'collection'
    # there are cases where item has multiple collection assignments
    for l in csv_file.readlines():
        id, col, rest = l.split(",", 2)
        col = col.strip('"')
        if col != "collection" and collection not in col:
            raise Exception(
                "{} contains entry for collection '{}', expecting entries for '{}' only".format(
                    csv_file.name, col, collection
                )
            )
    csv_file.seek(0)


def export_metadata(collection):
    bak_file = col_file(collection, "before-import")
    print("Exporting {} to {}".format(collection, bak_file))
    cmd = "{}/bin/dspace metadata-export --all -f {} -i {}".format(
        __DSPACE_HOME__, bak_file, collection
    )
    systm(cmd)


def index_optimize():
    print("Optimizing solr index")
    cmd = "{}/bin/dspace index-discovery  -o".format(__DSPACE_HOME__)
    systm(cmd)


def import_metadata(csv_file, collection):
    print("Importing {}".format(csv_file.name))
    cmd = "{}/bin/dspace metadata-import --silent -f {}".format(
        __DSPACE_HOME__, csv_file.name
    )
    try:
        systm(cmd)
        imprt_file = cp_file(csv_file, collection)
        print("Copyied {} to {}".format(csv_file.name, imprt_file))
    except Exception as e:
        raise e


def cp_file(csv_file, collection):
    cp_file = col_file(collection, "import")
    with open(cp_file, "w") as w:
        w.write(csv_file.read())
    csv_file.seek(0)
    return cp_file


def col_file(collection, ext):
    global __DSPACE_HOME__, __REPORT_PATH__, __RUN_ID__

    dir_name = "{}/{}".format(__DSPACE_HOME__, __REPORT_PATH__)
    mkdirpath(dir_name)
    bak_file = "{}/{}-{}-{}.csv".format(
        dir_name, collection.replace("/", "-"), __RUN_ID__, ext
    )
    return bak_file


def mangle_metadata(csv_file, tmpfile):
    replacement = "replace@{}".format(str(hex(random.randint(0, 4096))))
    data = csv_file.read().replace("REPLACE", replacement)
    tmpfile.write(data)
    tmpfile.seek(0)


def systm(cmd):
    print(cmd)
    sys.stdout.flush()
    status = os.system(cmd)
    if status != 0:
        raise Exception("FAILURE {}".format(cmd))
    return status


def env(key):
    if key in os.environ:
        return os.environ[key]
    else:
        raise Exception("Must set env var: {}".format(key))


def mkdirpath(dir_name):
    if os.path.isdir(dir_name):
        return
    dr = ""
    for p in dir_name.split("/"):
        if p:
            dr = dr + "/" + p
            if not os.path.isdir(dr):
                os.mkdir(dr)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__test__":
    import json

    for csv, col in json.loads(open("test_data/test_cases.json").read()):
        csv = open("test_data/{}".format(csv))
        with tempfile.NamedTemporaryFile() as tmp:
            mangle_metadata(csv, tmp)
            try:
                print(csv.name, col, tmp.name)
                main(tmp, col)
            except Exception as e:
                print(e)
                import traceback

                traceback.print_exc()
        print("++++++++++++++++++++++++++++\n")


if __name__ == "__main__":
    description = """
script imports metadata from given csv file into DSpace instance. 
It expects that the format matches the format produced when exporting 
collection metadata from the user interface. 

Before importing it checks that all metadata changes relate to items in the 
given collection and exports the current metadata to a dated backup file in 
$DSPACE_HOME/www/reports/metadata.
     
After successful import it copies the imported metadata to the same directory. 

Run with --solr option to optimize the index after succesfull metadata import.
"""

    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--solr", action="store_true", help="optimize solr index after import"
    )
    parser.add_argument("csv", type=file, help="csv file for dspace metadata imprt")
    parser.add_argument("collection", help="collecion handle")

    args = parser.parse_args()
    try:
        main(args.csv, args.collection, args.solr)
        sys.exit(0)
    except Exception as e:
        eprint(e)
