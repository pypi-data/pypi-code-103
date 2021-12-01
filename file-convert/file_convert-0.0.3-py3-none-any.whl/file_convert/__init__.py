import os
import re
import shutil
from tempfile import NamedTemporaryFile, mkdtemp
from typing import List
import subprocess


class FileConvert:
    @classmethod
    def create_destination_filepath(cls, suffix: str = None) -> str:
        file = NamedTemporaryFile(suffix=suffix)
        return file.name

    @classmethod
    def create_output_directory(cls) -> str:
        temporary_directory = mkdtemp()
        return temporary_directory

    @classmethod
    def syscall(cls, args: List[str]) -> str:
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate()
        if proc.returncode:
            raise Exception("Invalid return code")
        return stdout


class Doc(FileConvert):
    """Convert DOC(X) file to another formats"""

    def __init__(self, filepath: str):
        self._filepath = filepath

    @property
    def filepath(self) -> str:
        return self._filepath

    def to_pdf(self, dst_filepath: str = None) -> str:
        temporary_dir: str = mkdtemp()
        filepath_basename: str = os.path.basename(self.filepath)
        pdf_filename: str = os.path.join(temporary_dir, f"{os.path.splitext(filepath_basename)[0]}.pdf")
        super().syscall(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", temporary_dir, self.filepath])
        if dst_filepath is None:
            return pdf_filename
        shutil.move(pdf_filename, dst_filepath)
        return dst_filepath


class Pdf(FileConvert):
    """Convert PDF to another formats"""

    @classmethod
    def to_tiff_pages(cls, filepath: str, dst_directory: str = None) -> List[str]:
        pages: List[str] = []
        if dst_directory is None:
            dst_directory = cls.create_output_directory()
        command = ["pdftoppm", "-tiff", "-r", "300", filepath, f"{dst_directory}/page"]
        print(command)
        cls.syscall(command)
        for pdf_page in os.listdir(dst_directory):
            if re.match("^page-\d+\.tif$", pdf_page) is None:
                continue
            pages.append(os.path.join(dst_directory, pdf_page))
        return pages


class Tiff(FileConvert):
    """Convert tiff files to other formats"""

    @classmethod
    def multi_page_to_single_page(cls, filepath: str, dst_filepath: str = None) -> str:
        if dst_filepath is None:
            dst_filepath = cls.create_destination_filepath(suffix='tif')
        page: str = f"{filepath}[0]"
        cls.syscall(['convert', '-quiet', page, dst_filepath])
        return dst_filepath

    @classmethod
    def to_jp2(cls, filepath: str, dst_filepath: str = None, keep_metadata: bool = True) -> str:
        if dst_filepath is None:
            dst_filepath = cls.create_destination_filepath(suffix='jp2')
        cls.syscall(['opj_compress', '-i', filepath, '-o', dst_filepath])
        if keep_metadata:
            cls.syscall(['exiftool', '-overwrite_original_in_place', '-tagsFromFile', filepath, dst_filepath])
        return dst_filepath


class Jpeg2000(FileConvert):
    """Convert jpeg2000 files to other formats"""

    @classmethod
    def to_jp2(cls, filepath: str, dst_filepath: str = None) -> str:
        if dst_filepath is None:
            dst_filepath = cls.create_destination_filepath(suffix='tif')
        cls.syscall(['opj_decompress', '-i', filepath, '-o', dst_filepath])
        return dst_filepath
