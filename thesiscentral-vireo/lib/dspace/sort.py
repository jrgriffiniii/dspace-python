from lxml import etree as ET

import argparse
import datetime
import logging
import traceback
import os
import shutil
import sys

from ..vireo import VireoSheet


class ArgParser(argparse.ArgumentParser):
    @staticmethod
    def create():
        description = """
read thesis submission info from file given in --thesis option 

based on a submission status,  move submission aip directoies into sub-directories
"""
        loglevels = ["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG", "NOTSET"]

        parser = ArgParser(
            description=description, formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument(
            "--thesis", "-t", required=True, help="excel export file from vireo"
        )
        parser.add_argument("--aips", required=True, help="directory with DSPace AIPS")
        parser.add_argument(
            "--loglevel",
            "-l",
            choices=loglevels,
            default=logging.INFO,
            help="log level  - default: ERROR",
        )
        return parser

    def parse_args(self):
        args = argparse.ArgumentParser.parse_args(self)
        if not os.path.isdir(args.aips):
            raise Exception("%s is not a directory" % args.aips)
        return args


class SortByStatus:
    @staticmethod
    def build_logger():
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        return logger

    def __init__(self, submissions, aip_dir):
        self.error = 0
        self.submissions = submissions
        self.aip_dir = aip_dir

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

        logger = SortByStatus.build_logger()

        for sub_id in self.submissions.id_rows:
            cells = self.submissions.id_rows[sub_id]
            vals = VireoSheet.row_values(cells[0])

            id_cell_value = float(vals[idx])
            sub_id = int(id_cell_value)

            # This uses the "Status" value in the new subdirectory name
            status_value = vals[status_idx].replace(" ", "-")

            multi_author = vals[multi_author_idx]

            if multi_author.upper() == "YES":
                sub_dir_name = os.path.join(self.aip_dir, "Multi-Author", status_value)
            else:
                sub_dir_name = os.path.join(self.aip_dir, status_value)

            if not os.path.exists(sub_dir_name):
                os.makedirs(sub_dir_name)

            submission_dir_name = "submission_{}".format(sub_id)
            vireo_export_dir = os.path.join(
                self.aip_dir, "DSpaceSimpleArchive", submission_dir_name
            )
            dspace_package_dir = os.path.join(sub_dir_name, submission_dir_name)

            logger.info("Processing {} for {}...".format(sub_id, vireo_export_dir))

            if not os.path.exists(dspace_package_dir):
                shutil.move(vireo_export_dir, dspace_package_dir)

            logger.info("Processed {} into {}...".format(sub_id, dspace_package_dir))


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

    except Exception as e:
        logging.error(str(e))

        logging.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
