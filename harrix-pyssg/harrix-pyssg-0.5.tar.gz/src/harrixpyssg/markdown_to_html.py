from pathlib import Path
import shutil
import markdown

from .article import Article

import harrixpylib as h


class MarkdownToHtml:
    def __init__(self, markdown_filename, output_path):
        self.markdown_filename = Path(markdown_filename)
        self.output_path = Path(output_path)
        self.article = Article()
        self._dirs_of_files = ["img", "files", "demo", "gallery"]
        self._featured_image_extensions = ["webp", "jpg", "png"]

    def start(self):
        h.clear_directory(self.output_path)

        markdown_text = h.open_file(self.markdown_filename)

        md = markdown.Markdown(extensions=["meta"])
        html = md.convert(markdown_text)
        path_html = self.output_path / "index.html"
        self.article.meta = md.Meta
        self.article.md = h.remove_yaml_from_markdown(markdown_text)
        self.article.path_html = path_html
        self.article.html = html

        self.copy_dirs()
        self.copy_featured_image()
        # attribution

        h.save_file(html, self.output_path / "index.html")

    def copy_dirs(self):
        for d in self._dirs_of_files:
            self.copy_dir(d)

    def copy_dir(self, directory):
        path_img = self.markdown_filename.parent / directory
        if path_img.is_dir():
            shutil.copytree(path_img, self.output_path / directory, dirs_exist_ok=True)

    def copy_featured_image(self):
        for ext in self._featured_image_extensions:
            path = self.markdown_filename.parent / f"featured-image.{ext}"
            # print(path)
            if path.is_file():
                shutil.copy(path, self.output_path)
                output_path = self.output_path / f"featured-image.{ext}"
                self.article.featured_image = output_path
        path = self.markdown_filename.parent / "featured-image.svg"
        if path.is_file():
            shutil.copy(path, self.output_path)
            output_path = self.output_path / "featured-image.svg"
            self.article.featured_image_svg = output_path
