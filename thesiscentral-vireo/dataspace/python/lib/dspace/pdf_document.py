import os

class PDFDocument:

    def __init__(self, path, original_pdf_path, cover_pdf_path):
        self._path = path
        self._original_pdf_path = original_pdf_path
        self._cover_pdf_path = cover_pdf_path

    def generate_gs_command(self):
        segments = ["/usr/bin/env", "gs", "-dBATCH", "-dNOPAUSE", "-q", "-sDEVICE=pdfwrite", "'-sOutputFile=%s'".format(str(self._path)), str(self._cover_pdf_path), str(self._original_pdf_path)]
        return segments.join(' ')

    def generate_pdf(self):
        gs_command = generate_gs_command()
        return_code = os.system(gs_command)
        if (return_code != 0)
            raise StandardError("Failed to generate the PDF: %s".format(gs_command))
        return pdf_path

