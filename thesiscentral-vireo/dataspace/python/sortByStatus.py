
from lxml import etree as ET

import argparse

import datetime
import logging
import traceback
import os
import sys

# for the benefit of IDE import two ways
try:
    from vireo import VireoSheet
except Exception:
    from .vireo import VireoSheet

class ArgParser(argparse.ArgumentParser):
    @staticmethod
    def create():
        description = """
read thesis submission info from file given in --thesis option 

based on a submission status,  move submission aip directoies into sub-directories
"""
        loglevels = ['CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'NOTSET']

        parser = ArgParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("--thesis", "-t", required=True, help="excel export file from vireo")
        parser.add_argument("--aips",  required=True, help="directory with DSPace AIPS")
        parser.add_argument("--loglevel", "-l", choices=loglevels,  default=logging.INFO, help="log level  - default: ERROR")
        return parser;

    def parse_args(self):
        args= argparse.ArgumentParser.parse_args(self)
        if not os.path.isdir(args.aips):
            raise Exception("%s is not a directory" % args.aips)
        return args

class SortByStatus():
    def __init__(self, submissions, aip_dir):
        self.error = 0
        self.aip_dir = aip_dir
        self.submissions = submissions

    def sort_by_status(self):
        """
        raise an exception if there is no aip directory for one of the submissions
        move submission directories into aip subdirectories with same name as submission's status
        create subdirectories as needed

        :param aip_dir:   path to directory with DSpace aio subdirectories
        """
        idx = self.submissions.col_index_of(VireoSheet.ID)
        status_idx = self.submissions.col_index_of(VireoSheet.STATUS)
        department_idx = self.submissions.col_index_of(VireoSheet.DEPARTMENT)
        multi_author_idx = self.submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
        for sub_id in self.submissions.id_rows:
            vals = VireoSheet.row_values(self.submissions.id_rows[sub_id][0])
            sub_id = int(float(vals[idx]))
            if (vals[multi_author_idx].upper() == "YES"):
                subdir = 'Multi-Author'
            else:
                subdir = ''
            subdir = subdir + "/" + vals[status_idx].replace(' ', '-')
            dept = vals[department_idx]
            #print(sub_id, vals[multi_author_idx].upper(), subdir)
            sub_dir_name = "%s/%s/%s" % ( self.aip_dir, subdir, dept.replace(" ", "_"))
            if not os.path.exists(sub_dir_name):
                os.makedirs(sub_dir_name)
            cur_dir = "%s/submission_%d" % (self.aip_dir, sub_id)
            new_dir = "%s/submission_%d" % (sub_dir_name, sub_id)
            os.rename(cur_dir, new_dir)


def main():
    try:
        parser = ArgParser.create()
        args = parser.parse_args()

        logging.getLogger().setLevel(args.loglevel)
        logging.basicConfig()

        submissions = VireoSheet.createFromExcelFile(args.thesis)
        submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
        submissions.log_info()

        sorter = SortByStatus(submissions, args.aips)
        sorter.sort_by_status()
        sys.exit(0)

    except Exception as e:
        logging.error(str(e))

        logging.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
