import logging
from pathlib2 import Path
import os
import shutil
import zipfile
import tarfile
import pdb
import sys


def build_logger(loglevel):

    logger = logging.getLogger("dspace")
    logger.setLevel(loglevel)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(loglevel)
    logger.addHandler(console_handler)

    return logger


def generate_directory_name(department):
    value = None
    value = department.lower()
    value = value.replace(" ", "_")
    value = value.replace("&", "and")

    return value


def build_directory_path(department):
    dir_name = generate_directory_name(department)
    path = Path("export", dir_name)

    return path


def find_vireo_spreadsheet(department):
    dir_path = build_directory_path(department)
    path = dir_path.joinpath("ExcelExport.xlsx")

    return path


def find_restrictions_spreadsheet(department):
    dir_path = build_directory_path(department)
    path = dir_path.joinpath("RestrictionsWithId.xlsx")

    return path


def find_vireo_dspace_package(department):
    dir_path = build_directory_path(department)
    path = dir_path.joinpath("DSpaceSimpleArchive.zip")

    return path


def find_cover_page():
    path = Path("export", "SeniorThesisCoverPage.pdf")

    return path


def find_programs_spreadsheet(department):
    dir_path = build_directory_path(department)
    path = dir_path.joinpath("AdditionalPrograms.xlsx")

    return path


def find_authorizations_spreadsheet(department):
    dir_path = build_directory_path(department)
    path = dir_path.joinpath("ImportRestrictions.xlsx")

    return path


def extract_dspace_export(department):

    dir_path = build_directory_path(department)
    zip_file_path = dir_path.joinpath("DSpaceSimpleArchive.zip")

    with zipfile.ZipFile(str(zip_file_path), "r") as zip_ref:
        zip_ref.extractall(str(dir_path))

    return True
