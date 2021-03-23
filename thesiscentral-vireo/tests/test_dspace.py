import unittest
import pytest

import logging
from pathlib2 import Path

# Ensuring that the module dependencies can be imported
import sys

sys.path.append(".")

from lib.dspace import *


class DspaceTest(unittest.TestCase):
    def test_build_logger(self):
        built = build_logger(logging.INFO)
        self.assertIsInstance(built, logging.Logger)

    def test_generate_directory_name(self):
        output = generate_directory_name("Independent Concentration")
        assert output == "independent_concentration"

        output2 = generate_directory_name("Ops Research & Financial Engr")
        assert output2 == "ops_research_and_financial_engr"

    def test_build_directory_path(self):
        built = build_directory_path("Independent Concentration")
        self.assertIsInstance(built, Path)
        assert str(built) == "export/independent_concentration"

        built2 = build_directory_path("Ops Research & Financial Engr")
        self.assertIsInstance(built2, Path)
        assert str(built2) == "export/ops_research_and_financial_engr"

    def test_find_vireo_spreadsheet(self):
        found = find_vireo_spreadsheet("Independent Concentration")
        self.assertIsInstance(found, Path)
        assert str(found) == "export/independent_concentration/ExcelExport.xlsx"

    def test_find_restrictions_spreadsheet(self):
        found = find_restrictions_spreadsheet("Independent Concentration")
        self.assertIsInstance(found, Path)
        assert str(found) == "export/independent_concentration/RestrictionsWithId.xlsx"

    def test_find_vireo_dspace_package(self):
        found = find_vireo_dspace_package("Independent Concentration")
        self.assertIsInstance(found, Path)
        assert str(found) == "export/independent_concentration/DSpaceSimpleArchive.zip"

    def test_find_cover_page(self):
        found = find_cover_page()
        self.assertIsInstance(found, Path)
        assert str(found) == "export/SeniorThesisCoverPage.pdf"

    def test_programs_spreadsheet(self):
        found = find_programs_spreadsheet("Independent Concentration")
        self.assertIsInstance(found, Path)
        assert str(found) == "export/independent_concentration/AdditionalPrograms.xlsx"

    def test_authorizations_spreadsheet(self):
        found = find_authorizations_spreadsheet("Independent Concentration")
        self.assertIsInstance(found, Path)
        assert str(found) == "export/independent_concentration/ImportRestrictions.xlsx"

    def test_extract_dspace_export(self):
        result = extract_dspace_export("Test Department")
        assert result is True
        extracted_dir_path = Path("export", "test_department", "Approved")
        assert extracted_dir_path.exists()
