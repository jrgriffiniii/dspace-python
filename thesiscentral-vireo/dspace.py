import click
import logging
import os
from pathlib2 import Path
import pdb
import shutil
import sys
import tarfile
import zipfile

from lib.vireo.submission import PDFDocument

from lib.dspace.enhance_aips import VireoSheet, EnhanceAips
from lib.dspace.package import PackageCollection
from lib.dspace.restrictions import matchIds
from lib.dspace.sort import SortByStatus

# This is for the global functions - this should be refactored
from lib.dspace import *


def generate_package(
    department, thesis, add_certs, restrictions, aips, cover_page, loglevel
):
    """
    Generates a DSpace simple archive package.

    Attributes
    ----------
    department : string
        The name of the department
    thesis : string
        The path to the Vireo metadata spreadsheet export
    add_certs : string
        Foo
    restrictions : string
        The path to the restrictions Excel spreadsheet
    aips : string
        The path to the .zip
    cover_page : string
        The path to the cover page PDF
    loglevel : int
        The level of the logging

    Returns
    -------
    bool
        Whether or not the package was successfully created
    """
    logging.getLogger().setLevel(loglevel)
    logging.basicConfig()

    # Fixes problems on the tcsh
    escaped_thesis = thesis.replace("\\", "")
    thesis = escaped_thesis

    submissions = VireoSheet.createFromExcelFile(escaped_thesis)
    submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
    submissions.log_info()

    # Handle the certs file path
    escaped_certs = add_certs.replace("\\", "")
    add_certs = escaped_certs

    # Handle the more certs path
    moreCerts = submissions.readMoreCerts(escaped_certs, check_id=False)
    moreCerts.log_info()

    # Handle the restrictions path
    escaped_restrictions = restrictions.replace("\\", "")
    restrictions = escaped_restrictions

    restrictions = submissions.readRestrictions(escaped_restrictions, check_id=False)
    restrictions.log_info()

    enhancer = EnhanceAips(submissions, aips, cover_page)

    enhancer.addCertificates(moreCerts)
    enhancer.addRestrictions(restrictions)
    enhancer.print_table(file=sys.stdout)
    enhancer.adjust_aips()
    if enhancer.error > 0:
        raise RuntimeError("%s errors" % enhancer.error)
        sys.exit(0)

    return True


def update_package_metadata(department):

    dir_path = build_directory_path(department)
    dept_metadata_path = dir_path.joinpath("ExcelExport.xlsx")

    thesis = find_vireo_spreadsheet(department)
    submissions = VireoSheet.createFromExcelFile(str(dept_metadata_path))
    submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
    submissions.log_info()

    sorter = SortByStatus(submissions, str(dir_path))
    sorter.sort_by_status()

    return True


@click.group()
@click.option(
    "-d",
    "--department",
    required=True,
    prompt="Department",
    help="The department being exported",
)

# @click.option("--loglevel",
#                type=click.Choice([logging.WARN, logging.INFO, logging.DEBUG], case_sensitive=False),
#                default=logging.INFO,
#                help="Verbosity")


@click.pass_context
def cli(ctx, department):
    """"""

    ctx.ensure_object(dict)
    ctx.obj["DEPARTMENT"] = department


@cli.command()
@click.pass_context
def init_package(ctx):
    """"""

    department = ctx.obj["DEPARTMENT"]
    force_file_updates = True

    dir_path = build_directory_path(department)
    if not dir_path.exists():
        os.mkdir(str(dir_path))

    dir_name = generate_directory_name(department)

    dept_package_path = dir_path.joinpath("DSpaceSimpleArchive.zip")
    if not dept_package_path.exists():
        export_package_path = Path(
            "thesiscentral-exports", "dspace_packages", "{}.zip".format(dir_name)
        )
        shutil.copy(str(export_package_path), str(dept_package_path))

    extract_dspace_export(department)

    dept_metadata_path = dir_path.joinpath("ExcelExport.xlsx")
    if not dept_metadata_path.exists():
        export_metadata_path = Path(
            "thesiscentral-exports", "metadata", "{}.xlsx".format(dir_name)
        )
        shutil.copy(str(export_metadata_path), str(dept_metadata_path))

    dept_authorizations_path = dir_path.joinpath("RestrictionsWithId.xlsx")
    # This needs to be a forced update if audit_restrictions has already been invoked
    if dept_authorizations_path.exists():
        os.remove(str(dept_authorizations_path))

    root_authorizations_path = Path("export", "RestrictionsWithId.xlsx")
    shutil.copy(str(root_authorizations_path), str(dept_authorizations_path))

    dept_restrictions_path = dir_path.joinpath("ImportRestrictions.xlsx")
    if force_file_updates or not dept_authorizations_path.exists():
        root_restrictions_path = Path("export", "ImportRestrictions.xlsx")
        shutil.copy(str(root_restrictions_path), str(dept_restrictions_path))

    dept_programs_path = dir_path.joinpath("AdditionalPrograms.xlsx")
    if not dept_programs_path.exists():
        root_programs_path = Path("export", "AdditionalPrograms.xlsx")
        shutil.copy(str(root_programs_path), str(dept_programs_path))

    return True


@cli.command()
@click.pass_context
def regenerate_pdfs(ctx):
    department = ctx.obj["DEPARTMENT"]

    collection = PackageCollection.build(department)
    collection.regenerate_pdfs()


@cli.command()
@click.pass_context
def compress_package(ctx):
    """"""

    department = ctx.obj["DEPARTMENT"]

    dir_path = build_directory_path(department)
    tar_file_name = generate_directory_name(department)
    tar_file_path = dir_path.joinpath("{}.tgz".format(tar_file_name))

    tar_file = tarfile.open(name=str(tar_file_path), mode="w:gz")

    # This varies depending upon the structure of the Vireo export
    multi_author_dir_path = dir_path.joinpath("Multi-Author", "Approved")
    approved_dir_path = dir_path.joinpath("Approved")

    if multi_author_dir_path.exists():
        tar_file.add(str(multi_author_dir_path))

    if approved_dir_path.exists():
        tar_file.add(str(approved_dir_path))

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
def audit_restrictions(ctx):

    department = ctx.obj["DEPARTMENT"]

    dept_metadata_path = find_vireo_spreadsheet(department)

    submissions = VireoSheet.createFromExcelFile(str(dept_metadata_path))
    submissions.col_index_of(VireoSheet.MULTI_AUTHOR)
    submissions.log_info()

    root_authorizations_path = Path("export", "RestrictionsWithId.xlsx")
    restrictions = submissions.readRestrictions(
        str(root_authorizations_path), check_id=False
    )
    restrictions.log_info()

    loglevel = logging.INFO
    logger = build_logger(loglevel)

    matchIds(submissions, restrictions, logger)


@cli.command()
@click.pass_context
def rebuild_package_metadata(ctx):
    department = ctx.obj["DEPARTMENT"]

    # This needs to be a CLI argument
    loglevel = logging.INFO
    logger = build_logger(loglevel)

    status = update_package_metadata(department)

    return status


@cli.command()
@click.pass_context
def build_package(ctx):
    """"""

    department = ctx.obj["DEPARTMENT"]

    status = ctx.forward(audit_restrictions)

    # This needs to be a CLI argument
    loglevel = logging.INFO
    logger = build_logger(loglevel)

    status = ctx.forward(init_package)

    thesis = find_vireo_spreadsheet(department)
    aips = build_directory_path(department)

    add_certs = find_programs_spreadsheet(department)
    restrictions = find_authorizations_spreadsheet(department)
    cover_page = find_cover_page()

    # Generate the SIP
    status = generate_package(
        department,
        str(thesis),
        str(add_certs),
        str(restrictions),
        str(aips),
        str(cover_page),
        loglevel,
    )

    status = update_package_metadata(department)

    status = ctx.forward(compress_package)

    return status


if __name__ == "__main__":
    cli(obj={})
