from lxml import etree as ET

import argparse
import datetime
import logging
import traceback
import os
import sys
from shutil import copyfile
import pdb

# for the benefit of IDE import two ways
try:
    from vireo import VireoSheet
except Exception as import_error:
    pdb.set_trace()
    from . import vireo
    from vireo import VireoSheet

class ArgParser(argparse.ArgumentParser):
    @staticmethod
    def create():
        description = """
read thesis submission info from file given in --thesis option 
read additional certificate programs from  --add_certs file 
read access restriction info from --restrictions file 

warn when encountering a multi author thesis 

enhance pu-metadata.xml in AIPS in submission_<ID> subdirections of export directory where needed
"""
        loglevels = ['CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'NOTSET']

        parser = ArgParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("--thesis", "-t", required=True, help="excel export file from vireo")
        parser.add_argument("--add_certs", "-a", required=True, help="excel spreadsheet with additional certificate program info")
        parser.add_argument("--restrictions", "-r", required=True, help="TODO access restrictions")
        parser.add_argument("--aips",  required=True, help="directory with DSPace AIPS")
        parser.add_argument("--cover_page", "-c",  required=True, help="cwpdf cover page to glue pon 'top' of primary submission pdf")
        parser.add_argument("--loglevel", "-l", choices=loglevels,  default=logging.INFO, help="log level  - default: ERROR")
        return parser;

    def parse_args(self):
        args = argparse.ArgumentParser.parse_args(self)
        escaped = args.aips.replace('\\','')
        args.aips = escaped

        if not os.path.isdir( escaped ):
            raise Exception("%s is not a directory" % escaped)
        return args

class EnhanceAips:
    """
    Class for combining data from several Excel Spreadsheets and generating the output DSpace archival information packages (AIPs).

    Attributes
    ----------
    aip_dir : string
        The directory for the AIP packages to be written

    cover_pdf_path : string
        The directory path for the PDF cover generation

    submissions : VireoSheet
        The VireoSheet for tracking thesis submissions in a spreadsheet

    submissions_tbl : list
        A nested list copying the submission record values, along with the metadata extracted from the permissions and requirements spreadsheets

    walkin_idx : int
        The column index for the Mudd walk-in restriction permissions

    embargo_idx : int
        The column index for the embargo spreadsheet

    classyear : int
        The graduating class year of the thesis submissions

    """
    EXPORT_STATUS = ['Approved']
    WALKIN_MSG = 'Walk-in Access. This thesis can only be viewed on computer terminals at the <a href=http://mudd.princeton.edu>Mudd Manuscript Library</a>.'
    GLUE_CMD ="gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite \"-sOutputFile=%s\" %s %s"

    def __init__(self, submissions, aip_dir, pdf_cover_page):
        self.error = 0
        self.aip_dir = aip_dir
        self.cover_pdf_path = pdf_cover_page
        self.submissions = submissions
        self.submissions_tbl = self._make_submission_table()
        self.walkin_idx = len(self.submissions_tbl[0]) -1
        self.embargo_idx = self.walkin_idx - 1
        self.classyear = datetime.datetime.now().year

        self._confirm_aip_export_dir()

    def print_table(self, sep="\t", file=sys.stdout):
        print(sep.join(self.submissions.col_names() + [VireoSheet.R_EMBARGO, VireoSheet.R_WALK_IN]))
        for row in self.submissions_tbl:
            print(sep.join(unicode(x) for x in row))

    def _make_submission_table(self):
        aip_tbl = []
        idx = self.submissions.col_index_of(VireoSheet.ID)
        stud_idx = self.submissions.col_index_of(VireoSheet.STUDENT_NAME)
        cp_idx = self.submissions.col_index_of(VireoSheet.CERTIFICATE_PROGRAM)
        multi_idx = self.submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
        for sub_id in self.submissions.id_rows:
            current_rows = self.submissions.id_rows[sub_id]
            current_row = current_rows[0]

            vals = VireoSheet.row_values(current_row)

            normal_row_values = float(vals[idx])
            vals[idx] = int(normal_row_values)
            vals[multi_idx] = vals[multi_idx].upper() == "YES"
            #vals[stud_idx] = [ vals[stud_idx] ]

            cp = vals[cp_idx]
            vals[cp_idx] =  [cp] if (cp) else []
            logging.debug("\t".join(unicode(_) for _ in vals) + "\n")

            # add two cols at end for walkin and embargo restrictions
            aip_tbl.append(vals + [None, None])

        return aip_tbl


    def _confirm_aip_export_dir(self):
        """
        raise an exception if there is no aip directory for one of the submissions

        :param aip_dir:   path to directory with DSpace aio subdirectories
        """
        idx = self.submissions.col_index_of(VireoSheet.ID)
        status_idx = self.submissions.col_index_of(VireoSheet.STATUS)
        for row in self.submissions_tbl:
            if (row[status_idx] in EnhanceAips.EXPORT_STATUS):
                dir = "%s/DSpaceSimpleArchive/submission_%d" % (self.aip_dir, row[idx])
                if not os.path.isdir(dir):
                    self._error("AIP dir %s: not a directory" % dir)
                else:
                    for file in ["contents", "dublin_core.xml", "metadata_pu.xml", "LICENSE.txt"]:
                        fname = "%s/%s" % (dir, file)
                        if not os.path.isfile(fname) or not os.access(fname, os.R_OK):
                            if (file != "LICENSE.txt"):
                                self._error("AIP dir %s: can't read file %s" % (dir, file))
                            else:
                                logging.warning("AIP dir %s: can't read file %s - probably submittted by admin on behalf of student" % (dir, file))

    def _fix_multi_author(self):
        idx = self.submissions.col_index_of(VireoSheet.ID)
        status_idx = self.submissions.col_index_of(VireoSheet.STATUS)
        multi_idx = self.submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
        for sub in self.submissions_tbl:
            if sub[status_idx] in EnhanceAips.EXPORT_STATUS and sub[multi_idx]:
                logging.warning("submission: %d: skipping multi author thesis" % (sub[idx]))

    def addCertiticates(self, moreCerts):
        idx = self.submissions.col_index_of(VireoSheet.ID)
        cp_idx = self.submissions.col_index_of(VireoSheet.CERTIFICATE_PROGRAM)
        more_cp_idx = moreCerts.col_index_of(VireoSheet.CERTIFICATE_PROGRAM)
        for sub in self.submissions_tbl:
            sub_id = sub[idx]
            if (sub_id in moreCerts.id_rows):
                for row in moreCerts.id_rows[sub_id]:
                    pgm = VireoSheet.row_values(row)[more_cp_idx]
                    logging.info("ADDING cert program '%s' to submission with ID %d" %(pgm, sub[idx]))
                    sub[cp_idx].append(pgm)

    def addRestrictions(self, vireo_sheet):
        """
        Modifies the self.submissions variable, containing the VireoSheet instance for the departmental restrictions exported from the Department of the Registrar.

        Parameters
        ----------
        vireo_sheet : VireoSheet
            The VireoSheet object constructed from the Excel Spreadsheet for the restrictions.

        """

        idx = self.submissions.col_index_of(VireoSheet.ID)
        walkin_idx = vireo_sheet.col_index_of(VireoSheet.R_WALK_IN)
        embargo_idx = vireo_sheet.col_index_of(VireoSheet.R_EMBARGO)
        for sub in self.submissions_tbl:
            sub[self.embargo_idx] = 0
            sub[self.walkin_idx] = False
            sub_id = sub[idx]
            if (sub_id in vireo_sheet.id_rows):
                for row in vireo_sheet.id_rows[sub_id]:
                    sub[self.walkin_idx] = ("Yes" == row[walkin_idx].value)
                    if ( "N/A" == row[embargo_idx].value):
                        sub[self.embargo_idx] = 0
                    else:
                        sub[self.embargo_idx] = int(row[embargo_idx].value)
                    logging.info("ADDING restriction submission with ID %d: walkin %s, embargo %d" %(sub[idx], unicode(sub[self.walkin_idx]), sub[self.embargo_idx]))

    def adjust_aips(self):
        """
        This generates the XML files for the Princeton-specific and generic DSpace metadata. The self.submissions_tbl variable stores the combined data for the submissions, which are used to generate the XML Documents.

        """

        idx = self.submissions.col_index_of(VireoSheet.ID)

        for sub in self.submissions_tbl:
            logging.info("Processing submission %d" % (sub[idx]))
            try:
                glued = self._glue_cover_page(sub)
            except Exception as cover_page_error:
                pdb.set_trace()
                self._error("Exception submission aip: %d: %s" % (sub[idx], unicode(e)))
                logging.debug(traceback.format_exc())

            try:
                sub_xml = self._create_pu_xml(sub, glued)
                with open(self._xml_file_name(sub[idx], 'metadata_pu'), 'w') as f:
                    self._write_xml_file(sub_xml, f)
            except Exception as metadata_pu_error:
                import pdb; pdb.set_trace()
                self._error("Exception submission aip: %d: %s" % (sub[idx], unicode(e)))
                logging.debug(traceback.format_exc())

            try:
                with open(self._xml_file_name(sub[idx], 'dublin_core'), 'r') as f:
                    xml_content = f.read()
                    encoded_xml_content = xml_content.decode('utf-8').encode('ascii', 'ignore')
                    root = ET.fromstring(encoded_xml_content)

                    if self._adjust_dc_xml(root, sub):
                        with open(self._xml_file_name(sub[idx], 'dublin_core'), 'w') as f:
                            self._write_xml_file(root, f)
                    else:
                        logging.info("%s unchanged" % f.name)
            except Exception as dublin_core_error:
                import pdb; pdb.set_trace()
                self._error("Exception submission aip: %d: %s" % (sub[idx], unicode(e)))
                logging.debug(traceback.format_exc())


    def _glue_cover_page(self, sub):
        """
            return true cover was glued successfully
            return false if there was no primary doc to cover
            error out if glue operation fails
        """
        status_idx = self.submissions.col_index_of(VireoSheet.STATUS)
        sub_id = sub[self.submissions.col_index_of(VireoSheet.ID)]
        primary_path  = self._primary_doc_path(sub_id)
        if (not primary_path):
            logging.debug("submission %d has no primary document" % sub_id)
            if (sub[status_idx] in EnhanceAips.EXPORT_STATUS):
                logging.warning("submission %d has no primary document (status=%s)" % (sub_id, sub[status_idx]))
            return False

        copy_path = "%s/ORIG-%s" % (os.path.dirname(primary_path), os.path.basename(primary_path))
        if not os.path.isfile(copy_path):
            copyfile(primary_path, copy_path)

            escaped_copy_path = copy_path.replace(' ', '\ ')
            escaped_copy_path = escaped_copy_path.replace('&', '\&')

            cmd = EnhanceAips.GLUE_CMD % (primary_path, self.cover_pdf_path, escaped_copy_path)
            logging.debug(cmd)
            rc = os.system(cmd)

            if (rc != 0):
                self._error("***\nFAILED to exec: %s" % cmd)
            else:
                logging.info("%s covered" % primary_path)
        else:
            logging.info("%s already covered" % primary_path)
        return True

    def  _create_pu_xml(self, sub, glued):
        """
        This generates the Princeton-specific XML metadata for the DSpace AIP.

        Parameters
        ----------
        sub : list
            The list of values for the submission record

        glued : bool
            Whether or not there has been generated a PDF cover page for the thesis

        """
        author_id_idx = self.submissions.col_index_of(VireoSheet.STUDENT_ID)
        dept_idx = self.submissions.col_index_of(VireoSheet.DEPARTMENT)
        pgm_idx = self.submissions.col_index_of(VireoSheet.CERTIFICATE_PROGRAM)
        type_idx = self.submissions.col_index_of(VireoSheet.THESIS_TYPE)

        root = ET.Element('dublin_core', {'schema' : 'pu', 'encoding': "utf-8"})
        self._add_el(root, 'date.classyear', self.classyear)
        self._add_el(root, 'contributor.authorid', sub[author_id_idx])
        if (glued):
            self._add_el(root, 'pdf.coverpage', 'SeniorThesisCoverPage')
        if (sub[self.embargo_idx] > 0):
            self._add_el(root, 'embargo.terms', "%d-07-01"  % (self.classyear + sub[self.embargo_idx]))
        if (bool(sub[self.walkin_idx])):
            self._add_el(root, 'mudd.walkin', 'yes')
        if ('Department' in sub[type_idx]):
            self._add_el(root, 'department', self._department(sub[dept_idx]))
        for p in sub[pgm_idx]:
            self._add_el(root, 'certificate', p)
        return root

    def  _adjust_dc_xml(self, root, sub):
        changed = False
        if (sub[self.walkin_idx]):
            if (root.find('dcvalue[@element="rights"]') is None):
                self._add_el(root, 'rights.accessRights', EnhanceAips.WALKIN_MSG)
                changed = True
        logging.debug(" _adjust_dc_xml: changed=%s" % unicode(changed))
        return changed

    def _department(self, name):
        # remove everthing after '(' including '('
        name = name.rsplit('(', 1)[0]
        # replace & with and
        name = name.replace('&', 'and')
        # replace & with and
        name = name.replace('Engr', 'Engineering')
        return name

    def _add_el(self, root, metadata, value):
        logging.debug("XML add_el %s=%s" % (metadata, unicode(value)))
        splits = metadata.split('.')
        attrs = { 'element' : splits[0]}
        if len(splits) > 1:
            attrs['qualifier'] = splits[1]
        ET.SubElement(root, 'dcvalue', attrib=attrs).text = unicode(value)

    def _xml_file_name(self, sub_id, name):
        return "%s/DSpaceSimpleArchive/submission_%d/%s.xml" % (self.aip_dir, sub_id, name)

    def _primary_doc_path(self, sub_id):
        for line in open("%s/DSpaceSimpleArchive/submission_%d/contents" % ( self.aip_dir, sub_id)):
            if "primary:true" in line:
                return "%s/DSpaceSimpleArchive/submission_%d/%s" % (self.aip_dir, sub_id, line.split("\t")[0])
        return None

    def _write_xml_file(self, root, file):
        """
        Using a file handle, writes XML data into a file

        """
        logging.info("%s writing" % file.name)
        file_content = ET.tostring(root, encoding='utf8', method='xml', pretty_print=True)
        file.write(file_content)

    def _error(self, msg):
        logging.error(msg)
        self.error += 1

def main():
    parser = ArgParser.create()
    args = parser.parse_args()

    logging.getLogger().setLevel(args.loglevel)
    logging.basicConfig()

    escaped_thesis = args.thesis.replace('\\','')
    args.thesis = escaped_thesis

    submissions = VireoSheet.createFromExcelFile(escaped_thesis)
    submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
    submissions.log_info()

    # Handle the certs file path
    escaped_certs = args.add_certs.replace('\\','')
    args.add_certs = escaped_certs

    # Handle the more certs path
    moreCerts = submissions.readMoreCerts(escaped_certs, check_id=False)
    moreCerts.log_info()

    # Handle the restrictions path
    escaped_restrictions = args.restrictions.replace('\\','')
    args.restrictions = escaped_restrictions

    restrictions = submissions.readRestrictions(escaped_restrictions, check_id=False)
    restrictions.log_info()

    try:
        enhancer = EnhanceAips(submissions, args.aips, args.cover_page)

        enhancer.addCertiticates(moreCerts)
        enhancer.addRestrictions(restrictions)
        enhancer.print_table(file=sys.stdout)
        enhancer.adjust_aips()
        if ( enhancer.error > 0):
            raise RuntimeError("%s errors" % enhancer.error)
        sys.exit(0)

    except Exception as e:
        pdb.set_trace()
        logging.error(e)

        logging.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
