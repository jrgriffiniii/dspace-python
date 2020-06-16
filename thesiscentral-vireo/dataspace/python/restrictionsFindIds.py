import argparse

import logging
import traceback
import sys

# for the benefit of IDE import two ways
try:
    from vireo import VireoSheet
except Exception:
    from .vireo import VireoSheet


EXPORT_STATUS = ['Approved']

class ArgParser(argparse.ArgumentParser):
    @staticmethod
    def create():
        description = """
read thesis submission info from file given in --thesis option 
read access restriction info from --restrictions file 

fill ID column values where they are None with the submission ID of the matching thesis submission 

"""
        loglevels = ['CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'NOTSET']

        parser = ArgParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("--thesis", "-t", required=True, help="excel export file from vireo")
        parser.add_argument("--restrictions", "-r", required=True, help="TODO access restrictions")
        parser.add_argument("--loglevel", "-l", choices=loglevels,  default=logging.INFO, help="log level  - default: ERROR")
        return parser;

    def parse_args(self):
        args= argparse.ArgumentParser.parse_args(self)
        return args

def choose(matches, vireo, print_col_names):
    print("You have the following choices:")
    i = 0
    for m in matches:
        i = i + 1
        for p in print_col_names:
            idx = vireo.col_index_of(p)
            print("option %d --  %s" % (i, str(m[idx].value).strip()))
    choice = input("WHAT DO YOU WANT ? (return or now choice) > ").strip()
    try:
        id = int(choice)
        if (id > 0 and id <= i):
            return matches[id - 1]
        else:
            print("%d is invalid - try again" % id)
            return choose(matches, vireo, print_col_names)
    except Exception as e:
        print("never mind - try again later")
        return None

def save(vireo):
    choice = input("SAVE to File ? enter filename (return to not save) > ").strip()
    if ("" != choice):
        vireo.save(choice)
    else:
        vireo.save("/tmp/save.xlsx")

def vireoName(r_name):
    splts = r_name.split();
    return '%s, %s' % (splts[-1], splts[0])

def matchIds(submissions, restrictions):
    r_id_idx = restrictions.id_col
    r_name_idx = restrictions.col_index_of(VireoSheet.R_STUDENT_NAME)
    r_title_idx = restrictions.col_index_of(VireoSheet.R_TITLE)
    s_col_ids = [submissions.col_index_of(col) for col in [VireoSheet.STUDENT_NAME, VireoSheet.DOCUMENT_TITLE]]

    # iterator over rows in restrictions workbook
    # propose matches
    # update whith user choice
    iter = restrictions._sheet.iter_rows()
    _ = next(iter)  # throw header row away
    for row in iter:
        r_name = str(row[r_name_idx].value)
        print("----------------------------------------------")
        print("RESTRICTION Requested\n%s\n         --  %s" %(r_name,  str(row[r_title_idx].value)))
        s_id = row[r_id_idx].value
        if (None == s_id):
            s_name = vireoName( r_name )
            matches = submissions.matchingRows(VireoSheet.STUDENT_NAME, s_name)
            m = choose(matches, submissions, [VireoSheet.STUDENT_NAME, VireoSheet.DOCUMENT_TITLE])
            if (m != None): 
                row[r_id_idx].value = m[0].value
            print("--")
        else:
            match = submissions.id_rows[int(s_id)][0]
            print("\nMATCHED Submission")
            print("\n         --  ".join([str(match[id].value) for id in s_col_ids]))
            input("\nENTER to continue > ")
    print("----------------------------------------------")
    save(restrictions)

def main():

    try:
        parser = ArgParser.create()
        args = parser.parse_args()

        logging.getLogger().setLevel(args.loglevel)
        logging.basicConfig()

        submissions = VireoSheet.createFromExcelFile(args.thesis)
        submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
        submissions.log_info()

        restrictions = submissions.readRestrictions(args.restrictions, check_id=False)
        restrictions.log_info()

        matchIds(submissions, restrictions)


    except Exception as e:
        logging.error(e)
        logging.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
