import argparse

import logging
import traceback
import openpyxl

# for the benefit of IDE import two ways
try:
    from vireo import VireoSheet
except Exception:
    from .vireo import VireoSheet

def snippet():
    logging.getLogger().setLevel('INFO')
    # code snippet when in case you want to test in interactive python
    wb = openpyxl.load_workbook(filename = 'Thesis.xlsx')
    sheet = wb.worksheets[0]
    v = VireoSheet.createFromExcelFile('Thesis.xlsx')
    v.log_info()
    certs = v.readMoreCerts('AdditionalPrograms.xlsx')
    certs.log_info()
    return certs


class ArgParser(argparse.ArgumentParser):
    @staticmethod
    def create():
        description = """
read thesis submission info from file given in --thesis option 
if --add_certs option is given read info about additional certificate programs from file      

generate certificate program specific tsv files with submissions to the relevant program
home department submissions that have bo certificate program desifgnation are printed to the file None.tsv
"""
        loglevels = ['CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'NOTSET']

        parser = ArgParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("--thesis", "-t", default=None, required=True, help="excel export file from vireo")
        parser.add_argument("--split_col", "-s", required=False, default=VireoSheet.CERTIFICATE_PROGRAM, help="split column name - default %s" % VireoSheet.CERTIFICATE_PROGRAM)
        parser.add_argument("--add_certs", "-a", default=None, required=False, help="excel spreadsheet with additional certificate program info")
        parser.add_argument("--all_cols", "-A", action='store_true', help="include all columns in printout")
        parser.add_argument("--loglevel", "-l", choices=loglevels,  default=logging.INFO, help="log level  - default: ERROR")
        return parser;

    def parse_args(self):
        args= argparse.ArgumentParser.parse_args(self)
        return args


PRINT_COLUMNS = [VireoSheet.CERTIFICATE_PROGRAM, VireoSheet.STUDENT_NAME,
                 VireoSheet.DEPARTMENT, VireoSheet.SUBMISSION_DATE,
                 VireoSheet.ADVISORS, VireoSheet.DOCUMENT_TITLE, VireoSheet.PRIMARY_DOCUMENT]

def addToSplits(splits, split_on, split_data, submissions):
    logging.info("addToSplits %s data=%s submissions=%s" % (split_on, split_data.file_name, submissions.file_name))
    split_on_data_indx = split_data.col_index_of(split_on, required=True)
    sub_split_indx = submissions.col_index_of(split_on, required=True)
    for id in split_data.id_rows:
        matching_submission = submissions.id_rows[id][0]
        for data_row in split_data.id_rows[id]:
            col_val = data_row[split_on_data_indx].value
            if None == col_val:
                col_val = ''
            col_val = col_val.strip()
            add = [v for v in matching_submission]
            add[sub_split_indx] = data_row[split_on_data_indx]
            if not col_val in splits:
                splits[col_val] = [add]
            else:
                splits[col_val].append(add)

def print_splits(splits, print_col_names, print_col_ids):
    logging.info("#splits %d" % len(splits))
    for k in splits:
        _print_tsv(k, print_col_names, print_col_ids, splits[k])

def _print_tsv(name, col_names, col_ids, rows):
    file_name = name.replace(' ', '-')
    if not file_name:
        file_name = 'None'
    logging.info("%s: %d entries" % (file_name, len(rows)))
    out =open(file_name + ".tsv", 'w')
    # print header row
    print('\t'.join(col_names), file=out)
    # print rows with selected columns
    for row in rows:
        print('\t'.join(_select_row_values(row, col_ids)), file=out)
    out.close()


def _select_row_values(row, col_ids):
    sel_row = [row[i] for i in col_ids]
    return [(str(c.value) if None != c.value else 'None') for c in sel_row]


def main():

    try:
        parser = ArgParser.create()
        args = parser.parse_args()

        logging.getLogger().setLevel(args.loglevel)
        logging.basicConfig()

        submissions = VireoSheet.VireoSheet(args.thesis)
        submissions.log_info()

        splits = {}
        addToSplits(splits, split_on=args.split_col, split_data=submissions, submissions=submissions)

        if (args.add_certs):
            moreCerts = submissions.readMoreCerts(args.add_certs)
            addToSplits(splits, split_on=args.split_col, split_data=moreCerts, submissions=submissions)

        if (args.all_cols):
            print_col_names = submissions.col_names()
        else:
            # print cols that are in PRIN_COLUMNS and in submission's col_names
            print_col_names = list(filter(lambda x: x in submissions.col_names(), PRINT_COLUMNS))
        print_col_ids = [submissions.col_index_of(name, required=True)  for name in print_col_names]
        print_splits(splits, print_col_names, print_col_ids)

    except Exception as e:
        logging.error(e)
        logging.debug(traceback.format_exc())

if __name__ == "__main__":
    main()
