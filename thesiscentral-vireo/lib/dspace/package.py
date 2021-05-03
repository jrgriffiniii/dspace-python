class Package:
    def __init__(self, path):
        self._path = path

    def build_pdf_document(self):
        self._pdf_document = None

        self._pdf_document = PDFDocument()
        return self._pdf_document


class PackageCollection:
    def __init__(self, path):
        self._path = path

    def build_packages(self):
        self._packages = []

        return self._packages
