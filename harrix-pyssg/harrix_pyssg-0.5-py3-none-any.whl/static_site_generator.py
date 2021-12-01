from .dir_md_to_dir_html import DirMdToDirHtml

import harrixpylib as h


class StaticSiteGenerator:
    def __init__(self, markdown_paths, output_path, log=False):
        self.markdown_paths = markdown_paths
        self.output_path = output_path
        self.articles = list()

    def start(self):
        h.clear_directory(self.output_path)
        for path in self.markdown_paths:
            d = DirMdToDirHtml(path, self.output_path, True)
            d.start()
            self.articles += d.articles
        for article in self.articles:
            print(article.path_html)
