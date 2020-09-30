import argparse
import logging
import traceback
import sys
import os
import pdb

# For the benefit of IDE import two ways
try:
    from vireo import VireoSheet
except Exception as import_error:
    pdb.set_trace()
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

def choose(matches, vireo, print_col_names, logger):
    if(len(matches) < 1):
        return None

    logger.info("You have the following choices:")

    for m in matches:
        i = 0

        for p in print_col_names:
            i = i + 1
            try:
                idx = vireo.col_index_of(p)
                cell_value = m[idx].value.encode('utf-8')
                option_value = str(cell_value).strip()
                logger.info("option %d --  %s" % (i, option_value))
            except Exception as inst:
                import pdb; pdb.set_trace()
                pass

    choice_input = raw_input("WHAT DO YOU WANT ? (Only choose option 1) > ")
    choice = int(choice_input)

    try:
        if (choice > 0 and choice <= i):
            return matches[choice - 1]
        else:
            logger.error("%d is invalid - try again" % choice)
            return choose(matches, vireo, print_col_names, logger)
    except Exception as e:
        logger.error("An error has been encountered: %s" % e.message)
        return None

def save(vireo, logger):
    try:
        current_file_path = os.path.abspath(__file__)
        parent_directory = os.path.abspath(os.path.join(current_file_path, os.pardir))
        default_path = os.path.abspath(os.path.join( parent_directory, "export", "ImportRestrictions.xlsx" ))

        logger.info("Saving the updated authorizations files to {}".format(default_path))
        vireo.save(default_path)
    except Exception as inst:
        import pdb; pdb.set_trace()
        pass

def vireoName(r_name):
    splts = r_name.split();
    return '%s, %s' % (splts[-1], splts[0])

def matchIds(submissions, restrictions, logger):
    r_id_idx = restrictions.id_col
    r_name_idx = restrictions.col_index_of(VireoSheet.R_STUDENT_NAME)
    r_title_idx = restrictions.col_index_of(VireoSheet.R_TITLE)
    s_col_ids = [submissions.col_index_of(col) for col in [VireoSheet.STUDENT_NAME, VireoSheet.DOCUMENT_TITLE]]

    # Iterator over rows in restrictions workbook
    # propose matches
    # update whith user choice
    iter = restrictions._sheet.iter_rows()
    _ = next(iter)  # throw header row away
    for row in iter:
        r_name = row[r_name_idx].value.encode('utf-8')
        logger.debug("----------------------------------------------")
        title_value = row[r_title_idx].value.encode('utf-8')
        logger.debug("RESTRICTION Requested\n%s\n         --  %s" %(r_name, title_value))
        s_id = row[r_id_idx].value

        # If the ID needs to be assigned...
        if (None == s_id):
            s_name = vireoName( r_name )

            matches = submissions.matchingRows(VireoSheet.STUDENT_NAME, s_name)
            m = choose(matches, submissions, [VireoSheet.STUDENT_NAME, VireoSheet.DOCUMENT_TITLE], logger)

            if (len(matches) > 0 and m != None):
                row[r_id_idx].value = m[0].value
                logger.debug("The ID %s was matched" % (m[0].value))
            else:
                logger.debug("No ID matches were for found for %s" % (s_name))

            logger.debug("--")
        else:
            pdb.set_trace()
            match = submissions.id_rows[int(s_id)][0]
            logger.info("\nMATCHED Submission")
            logger.info("\n         --  ".join([str(match[id].value) for id in s_col_ids]))
            raw_input("\nENTER to continue > ")
    logger.debug("----------------------------------------------")
    save(restrictions, logger)

def build_logger(loglevel):
    logger = logging.getLogger('dspace.restrictionsFindIds')
    logger.setLevel(loglevel)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(loglevel)
    logger.addHandler(console_handler)

    return logger

def main():

    try:
        parser = ArgParser.create()
        args = parser.parse_args()

        logger = build_logger(args.loglevel)

        submissions = VireoSheet.createFromExcelFile(args.thesis)
        submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
        submissions.log_info()

        restrictions = submissions.readRestrictions(args.restrictions, check_id=False)
        restrictions.log_info()

        matchIds(submissions, restrictions, logger)

    except Exception as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
