import argparse
import logging
import traceback
import sys
import os
import pdb
from ..vireo import VireoSheet

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

def choose(matches, vireo, col_name, title_col_name, logger):
    """
    Queries the user over STDIN for a choice when multiple matches for submission restrictions are found.
    """

    if(len(matches) < 1):
        return None

    logger.info("You have the following choices:")

    for i, matching_row in enumerate(matches):
        try:
            col_index = vireo.col_index_of(col_name)
            cell = matching_row[col_index]
            cell_value = cell.value.encode('utf-8')

            title_col_index = vireo.col_index_of(title_col_name)
            title_cell = matching_row[title_col_index]
            title_cell_value = title_cell.value.encode('utf-8')

            option_value = str(cell_value)
            logger.info("Choice {}: {} ({})".format(i + 1, option_value.strip(), title_cell_value))
        except Exception as inst:
            import pdb; pdb.set_trace()
            pass

    choice_input = raw_input("> ")
    choice = int(choice_input)

    try:
        if (choice > 0 and choice < i):
            return matches[choice]
        else:
            logger.error("%d is invalid - try again" % choice)
            return choose(matches, vireo, print_col_names, logger)
    except Exception as e:
        logger.error("An error has been encountered: %s" % e.message)
        return None

def save(vireo, logger):
    """
    Save the updated restrictions spreadsheet to a new file
    """
    try:
        current_file_path = os.path.abspath(__file__)
        parent_directory = os.path.abspath(os.path.join(current_file_path, os.pardir, '..', '..'))
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
    """
    Given a number of Vireo submission spreadsheet rows, look to match these to any restrictions specified in a separate restrictions spreadsheet.
    """

    r_id_idx = restrictions.id_col
    r_name_idx = restrictions.col_index_of(VireoSheet.R_STUDENT_NAME)
    r_title_idx = restrictions.col_index_of(VireoSheet.R_TITLE)
    s_col_ids = [submissions.col_index_of(col) for col in [VireoSheet.STUDENT_NAME, VireoSheet.DOCUMENT_TITLE]]

    rows = restrictions._sheet.iter_rows()
    _ = next(rows)  # throw header row away

    for row in rows:
        r_name = row[r_name_idx].value.encode('utf-8')
        title_value = row[r_title_idx].value.encode('utf-8')
        logger.debug("Processing restriction record {} ({})...".format(title_value, r_name))
        submission_id = row[r_id_idx].value

        # This is for cases where the ID has not been set by a previous process
        if submission_id is None:
            author_name = vireoName( r_name )

            # Matching between the rows is accomplished by VireoSheet
            # This is attempted using the unique student name
            matches = submissions.matchingRows(VireoSheet.STUDENT_NAME, author_name)
            if len(matches) == 1:
                matching_row = matches[0]
            else:
                matching_row = choose(matches, submissions, VireoSheet.STUDENT_NAME, VireoSheet.DOCUMENT_TITLE, logger)

            if (len(matches) > 0 and matching_row != None):
                id_cell = matching_row[0]
                id_value = id_cell.value
                updated_cell = row[r_id_idx]
                updated_cell.value = id_value

                logger.debug("The ID {} was matched...".format(id_value))
            else:
                logger.debug("No ID matches were found for the author {}".format(author_name))
        else:

            # Should this be encountered?
            pdb.set_trace()

            matching_rows = submissions.id_rows[int(submission_id)]
            matching_row = matching_rows[0]
            matching_id_values = [ str(matching_row[i].value) for i in s_col_ids ]

            logger.debug("The IDs {} were matched...".format(matching_id_values.join("\n")))
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
