import argparse

import logging
import traceback
import sys
import os

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
    if(len(matches) < 1):
        return None

    print("You have the following choices:")

    for m in matches:
        i = 0

        for p in print_col_names:
            i = i + 1
            try:
                idx = vireo.col_index_of(p)
                cell_value = m[idx].value.encode('utf-8')
                option_value = str(cell_value).strip()
                print("option %d --  %s" % (i, option_value))
            except Exception as inst:
                import pdb; pdb.set_trace()
                pass

    choice = raw_input("WHAT DO YOU WANT ? (return or now choice) > ")
    try:
        if (choice > 0 and choice <= i):
            return matches[choice - 1]
        else:
            print("%d is invalid - try again" % choice)
            return choose(matches, vireo, print_col_names)
    except Exception as e:
        print("never mind - try again later")
        return None

def save(vireo):
    try:
        current_file_path = os.path.abspath(__file__)
        parent_directory = os.path.abspath(os.path.join(current_file_path, os.pardir))
        default_path = os.path.abspath(os.path.join( parent_directory, "ImportRestrictions.xlsx" ))

        choice_input = raw_input("SAVE to File ? enter filename (RETURN defaults to " + default_path + ") > ")
        choice = choice_input.strip()

        if ("" != choice):
            vireo.save(choice)
        else:
            vireo.save(default_path)
    except Exception as inst:
        import pdb; pdb.set_trace()
        pass

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
        r_name = row[r_name_idx].value.encode('utf-8')
        print("----------------------------------------------")
        title_value = row[r_title_idx].value.encode('utf-8')
        print("RESTRICTION Requested\n%s\n         --  %s" %(r_name, title_value))
        s_id = row[r_id_idx].value

        # If the ID needs to be assigned...
        if (None == s_id):
            s_name = vireoName( r_name )

            matches = submissions.matchingRows(VireoSheet.STUDENT_NAME, s_name)
            m = choose(matches, submissions, [VireoSheet.STUDENT_NAME, VireoSheet.DOCUMENT_TITLE])

            if (len(matches) > 0 and m != None):
                row[r_id_idx].value = m[0].value
                print("The ID %s was matched" % (m[0].value))
            else:
                print("No ID matches were for found for %s" % (s_name))

            print("--")
        else:
            match = submissions.id_rows[int(s_id)][0]
            print("\nMATCHED Submission")
            print("\n         --  ".join([str(match[id].value) for id in s_col_ids]))
            raw_input("\nENTER to continue > ")
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
