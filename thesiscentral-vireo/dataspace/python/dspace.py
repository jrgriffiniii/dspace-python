import click
import logging

from enhanceAips import VireoSheet, EnhanceAips


def generate_package(
        department,

        thesis,
        add_certs,
        restrictions,
        aips,
        cover_page,

        loglevel,

        ):
    """

    """
    logging.getLogger().setLevel(loglevel)
    logging.basicConfig()

    # Fixes problems on the tcsh
    escaped_thesis = thesis.replace('\\','')
    thesis = escaped_thesis

    submissions = VireoSheet.createFromExcelFile(escaped_thesis)
    submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
    submissions.log_info()

    # Handle the certs file path
    escaped_certs = add_certs.replace('\\','')
    add_certs = escaped_certs

    # Handle the more certs path
    moreCerts = submissions.readMoreCerts(escaped_certs, check_id=False)
    moreCerts.log_info()

    # Handle the restrictions path
    escaped_restrictions = restrictions.replace('\\','')
    restrictions = escaped_restrictions

    restrictions = submissions.readRestrictions(escaped_restrictions, check_id=False)
    restrictions.log_info()

    try:
        enhancer = EnhanceAips(submissions, aips, cover_page)

        enhancer.addCertiticates(moreCerts)
        enhancer.addRestrictions(restrictions)
        enhancer.print_table(file=sys.stdout)
        enhancer.adjust_aips()
        if (enhancer.error > 0):
            raise RuntimeError("%s errors" % enhancer.error)
        sys.exit(0)

    except Exception as e:
        pdb.set_trace()
        logging.error(e)

        logging.debug(traceback.format_exc())
        sys.exit(1)

def generate_directory_name(department):
    value = None
    value = department.lower()
    value = value.replace(' ', '_')
    value = value.replace('&', 'and')

    return value

def build_directory_path(department):
    dir_name = generate_directory_name(department)
    path = Path( 'export', dir_name)

    return path

def find_vireo_spreadsheet(department):
    dir_path = build_directory_path(department)
    path = dir_path.joinpath('ExcelExport.xlsx')

    return path

def find_restrictions_spreadsheet(department):
    dir_path = build_directory_path(department)
    path = dir_path.joinpath('RestrictionsWithId.xlsx')

    return path

def find_vireo_dspace_package(department):
    dir_path = build_directory_path(department)
    path = dir_path.joinpath('DSpaceSimpleArchive.zip')

    return path

def find_cover_page():
    path = Path('export', 'SeniorThesisCoverPage.pdf')

    return path

def prepare_files(department):
    """

    """

    dir_path = build_directory_path(department)
    os.mkdir(dir_path)

    dir_name = generate_directory_name(department)
    export_package_path = Path('thesiscentral-exports', 'dspace_packages', '%s.zip'.format(dir_name))
    export_metadata_path = Path('thesiscentral-exports', 'metadata', '%s.xlsx'.format(dir_name))

    dept_package_path = dir_path.joinpath('DSpaceSimpleArchive.zip')
    dept_metadata_path = dir_path.joinpath('ExcelExport.xlsx')

    shutil.copy(export_metadata_path, dept_metadata_path)
    shutil.copy(export_package_path, dept_package_path)

    root_authorizations_path = Path('export', 'RestrictionsWithId.xlsx')
    root_restrictions_path = Path('export', 'ImportRestrictions.xlsx')
    root_programs_path = Path('export', 'AdditionalPrograms.xlsx')

    dept_authorizations_path = dir_path.joinpath('RestrictionsWithId.xlsx')
    dept_restrictions_path = dir_path.joinpath('ImportRestrictions.xlsx')
    dept_programs_path = dir_path.joinpath('AdditionalPrograms.xlsx')

    shutil.copy(root_authorizations_path, dept_authorizations_path)
    shutil.copy(root_restrictions_path, dept_restrictions_path)
    return shutil.copy(root_programs_path, dept_programs_path)

@click.command()
@click.option('--department',
                prompt='Department',
                help='The department being exported')
@click.option("--loglevel",
                type=click.Choice([logging.WARN, logging.INFO, logging.DEBUG], case_sensitive=False),
                default=logging.INFO,
                help="Verbosity")
def export_department(department, loglevel):
    """

    """

    thesis = find_vireo_spreadsheet(department)
    aips = find_vireo_dspace_package(department)

    restrictions = find_restrictions_spreadsheet(department)
    cover_page = find_cover_page()

    prepare_files(department)

    # Generate the SIP
    status = generate_package(
        department,

        str(thesis),
        str(add_certs),
        str(restrictions),
        str(aips),
        str(cover_page),

        loglevel
    )

    return status

if __name__ == '__main__':
    export_department()
