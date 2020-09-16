import click
import logging
from pathlib2 import Path
import os
import shutil
import zipfile
import tarfile

import pdb
import sys

from enhanceAips import VireoSheet, EnhanceAips
from sortByStatus import SortByStatus

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

    enhancer = EnhanceAips(submissions, aips, cover_page)

    enhancer.addCertiticates(moreCerts)
    enhancer.addRestrictions(restrictions)
    enhancer.print_table(file=sys.stdout)
    enhancer.adjust_aips()
    if (enhancer.error > 0):
        raise RuntimeError("%s errors" % enhancer.error)
        sys.exit(0)

    return True

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

def find_programs_spreadsheet(department):
    dir_path = build_directory_path(department)
    path = dir_path.joinpath('AdditionalPrograms.xlsx')

    return path

def find_authorizations_spreadsheet(department):
    dir_path = build_directory_path(department)
    path = dir_path.joinpath('ImportRestrictions.xlsx')

    return path

def extract_dspace_export(department):

    dir_path = build_directory_path(department)
    zip_file_path = dir_path.joinpath('DSpaceSimpleArchive.zip')

    with zipfile.ZipFile(str(zip_file_path), "r") as zip_ref:
        zip_ref.extractall(str(dir_path))

    return True

def prepare_files(department):
    """

    """

    dir_path = build_directory_path(department)
    if not dir_path.exists():
        os.mkdir(str(dir_path))

    dir_name = generate_directory_name(department)

    dept_package_path = dir_path.joinpath('DSpaceSimpleArchive.zip')
    if not dept_package_path.exists():
        export_package_path = Path('thesiscentral-exports', 'dspace_packages', '%s.zip'.format(dir_name))
        shutil.copy(export_package_path, dept_package_path)

    extract_dspace_export(department)

    dept_metadata_path = dir_path.joinpath('ExcelExport.xlsx')
    if not dept_metadata_path.exists():
        export_metadata_path = Path('thesiscentral-exports', 'metadata', '%s.xlsx'.format(dir_name))
        shutil.copy(export_metadata_path, dept_metadata_path)

    dept_authorizations_path = dir_path.joinpath('RestrictionsWithId.xlsx')
    if not dept_authorizations_path.exists():
        root_authorizations_path = Path('export', 'RestrictionsWithId.xlsx')
        shutil.copy(root_authorizations_path, dept_authorizations_path)

    dept_restrictions_path = dir_path.joinpath('ImportRestrictions.xlsx')
    if not dept_restrictions_path.exists():
        root_restrictions_path = Path('export', 'ImportRestrictions.xlsx')
        shutil.copy(root_restrictions_path, dept_restrictions_path)

    dept_programs_path = dir_path.joinpath('AdditionalPrograms.xlsx')
    if not dept_programs_path.exists():
        root_programs_path = Path('export', 'AdditionalPrograms.xlsx')
        shutil.copy(root_programs_path, dept_programs_path)

    return True

def update_package_metadata(department):

    dir_path = build_directory_path(department)
    dept_metadata_path = dir_path.joinpath('ExcelExport.xlsx')

    thesis = find_vireo_spreadsheet(department)
    submissions = VireoSheet.createFromExcelFile(str(dept_metadata_path))
    submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
    submissions.log_info()

    sorter = SortByStatus(submissions, str(dir_path))
    sorter.sort_by_status()

    return True

@click.group()
@click.option('--department',
                prompt='Department',
                help='The department being exported')

#@click.option("--loglevel",
#                type=click.Choice([logging.WARN, logging.INFO, logging.DEBUG], case_sensitive=False),
#                default=logging.INFO,
#                help="Verbosity")

@click.pass_context
def cli(ctx, department):
    """
    """

    ctx.ensure_object(dict)
    ctx.obj['DEPARTMENT'] = department

@cli.command()
@click.pass_context
def compress_package(ctx):
    """
    """

    department = ctx.obj['DEPARTMENT']

    dir_path = build_directory_path(department)
    tar_file_name = generate_directory_name(department)
    tar_file_path = dir_path.joinpath(tar_file_name)

    tar_file = tarfile.open(name=str(tar_file_path), mode='w:gz')

    sip_dir_path = dir_path.joinpath('Approved')
    tar_file.add(str(sip_dir_path))

    metadata_path = find_vireo_spreadsheet(department)
    tar_file.add(str(metadata_path))

    restrictions_path = find_restrictions_spreadsheet(department)
    tar_file.add(str(restrictions_path))

    programs_path = find_programs_spreadsheet(department)
    tar_file.add(str(programs_path))

    authorizations_path = find_authorizations_spreadsheet(department)
    tar_file.add(str(authorizations_path))

    tar_file.close()

    return tar_file

@cli.command()
@click.pass_context
def export_department(ctx):
    """

    """

    department = ctx.obj['DEPARTMENT']

    thesis = find_vireo_spreadsheet(department)
    aips = build_directory_path(department)

    add_certs = find_programs_spreadsheet(department)
    restrictions = find_restrictions_spreadsheet(department)
    cover_page = find_cover_page()

    prepare_files(department)

    # This needs to be a CLI argument
    loglevel=logging.INFO

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

    status = update_package_metadata(department)

    status = compress_package(department)

    return status

if __name__ == '__main__':
        cli(obj={})
