import logging
import os
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple, Union

import yaml
from functools import reduce
from jtex import DocModel, Tag

from curvenote.latex.TaggedContentCollection import TaggedContentCollection
from curvenote.latex.utils.decorators import log_and_raise_errors
from curvenote.models import BlockFormat, Project

from ..client import Session
from ..utils import decode_oxa_link, decode_url
from .LatexArticle import LatexArticle
from .utils import LocalMarker, escape_latex

logger = logging.getLogger()


class ProjectItem(NamedTuple):
    path: str
    filename: str
    article: LatexArticle


class LatexProject:
    """
    Responsible for project wide fetching and reconcilliation of content as a LaTeX project
    """

    def __init__(
        self,
        session: Session,
        target_folder: str,
        user_options: Dict[str, Any],
    ):
        self._session: Session = session
        self._user_options: Dict[str, Any] = user_options

        self._target_folder: str = os.path.abspath(target_folder)
        self._assets_folder: str = os.path.join(self._target_folder, "assets")
        self._images_folder: str = os.path.join(self._target_folder, "assets", "images")

        self.create_folders()

        self._project_items: List[ProjectItem] = []
        self._reference_list: List[LocalMarker] = []
        self._figure_list: List[LocalMarker] = []
        self._tagged_content: TaggedContentCollection = TaggedContentCollection()

    @classmethod
    def build_single_article_by_name(
        cls,
        target_folder: str,
        session: Session,
        project_id_or_obj: Union[str, Project],
        article_id: str,
        version: int,
        tex_format: BlockFormat,
        user_options: Dict[str, Any] = {},
    ):
        """
        Factory Method

        Creates a LatexProject, performs fetch and reconcillation and then returns
        that LatexProject object

        @param cls: The LatexProject class
        @param target_folder: The folder where the project will be created
        @param session: The current session
        @param project_id_or_obj: The ID of the project or the Project object
        @param article_id: The ID of the article
        @param version: The version of the article
        @param tex_format: The format of the article
        @param user_options: a dict of data that will correspond to user options available in the specified template
        @returns: A LatexProject object
        """
        latex_project = cls(session, target_folder, user_options)
        latex_project.add_article(project_id_or_obj, article_id, version, tex_format)
        latex_project.reconcile()
        return latex_project

    @classmethod
    def build_single_article_by_url(
        cls,
        target_folder: str,
        session: Session,
        url: str,
        tex_format: BlockFormat,
        user_options: Dict[str, Any] = {},
    ):
        """
        Factory Method
        Creates a LatexProject, performs fetch and reconcilillation and then returns
        that LatexProject object

        @param cls: The LatexProject class
        @param target_folder: The folder where the project will be created
        @param session: The current session
        @param url: The URL of the article
        @param tex_format: The format of the article
        @param user_options: a dict of data that will correspond to user options available in the specified template
        @returns: A LatexProject object
        """
        vid, pathspec = None, None
        try:
            vid = decode_oxa_link(url)
        except ValueError:
            pathspec = decode_url(url)

        latex_project = cls(session, target_folder, user_options)

        logging.info("Creating folder strcture in %s", {target_folder})
        latex_project.create_folders()

        if vid:
            latex_project.add_article(vid.project, vid.block, vid.version, tex_format)
        elif pathspec is not None:
            if not pathspec.block:
                raise ValueError("URL does not include a block id")
            latex_project.add_article(
                pathspec.project,
                pathspec.block,
                pathspec.version,
                tex_format,
            )
        else:
            raise ValueError("Invalid URL")

        latex_project.reconcile()
        return latex_project

    def create_folders(self):
        logger.info("Creating %s", self._assets_folder)
        os.makedirs(self._assets_folder, exist_ok=True)

        logger.info("Creating %s", self._images_folder)
        os.makedirs(self._images_folder, exist_ok=True)

    def next_index(self):
        return len(self._project_items)

    @log_and_raise_errors(lambda *args: "Could not add article to LaTeX project")
    def add_article(
        self,
        project_id: Union[str, Project],
        article_id: str,
        version: int,
        fmt: BlockFormat,
    ):
        logging.info("adding article using ids/names")
        latex_article = LatexArticle(self._session, project_id, article_id)
        latex_article.fetch(fmt, version)
        latex_article.localize(
            self._session,
            self._assets_folder,
            self._reference_list,
            self._figure_list,
        )
        filename = f"{self.next_index()}_{latex_article._block.name}"
        self._project_items.append(
            ProjectItem(
                path=f"documents/{filename}", article=latex_article, filename=filename
            )
        )
        logging.info("added article")

    def reconcile(self):
        for project_item in self._project_items:
            project_item.article.reconcile()

    def dump(self, allowed_tags: Set[Tag]) -> Tuple[DocModel, List[str], str]:
        logging.info("Dumping data and content...")
        if len(self._project_items) < 1:
            raise ValueError("Need at least one article")

        # TODO - in book mode (compact == False) we would need to
        # return a list of strings
        content: List[str] = []
        self._tagged_content = TaggedContentCollection()
        for project_item in self._project_items:
            latex_content, tagged = project_item.article.dump(allowed_tags)
            content.append(latex_content)
            self._tagged_content.merge(tagged)

        first = self._project_items[0]

        def is_corresponding(options, name):
            if not 'corresponding_author' in options:
                return False
            return reduce((lambda flag, item: flag or item["name"] == name), options["corresponding_author"], False)

        def corresponding_email(options, name):
            if not 'corresponding_author' in options:
                return False
            return reduce((lambda email, item: item["email"] if item["name"] == name else email), options["corresponding_author"], None)

        authors = []
        for author in first.article.authors:
            if author.user:
                user = next(
                    (u for u in first.article._users if u.id == author.user), None
                )
                if user:
                    authors.append(
                        dict(
                            username=user.username,
                            name=user.display_name,
                            bio=user.bio,
                            location=user.location,
                            website=user.website,
                            github=user.github,
                            twitter=user.twitter,
                            affiliation=user.affiliation,
                            orcid=user.orcid,
                            curvenote=f"https://curvenote.com/@{user.username}",
                            is_corresponding=is_corresponding(self._user_options, user.display_name),
                            email=corresponding_email(self._user_options, user.display_name)
                        )
                    )
            elif author.plain:
                authors.append(
                    dict(
                        name=escape_latex(author.plain),
                        is_corresponding=is_corresponding(self._user_options, author.plain)
                        )
                    )
            else:
                logging.info("found empty author, skipping...")


        SHORT_TITLE_SIZE = 30
        short_title = (
            first.article.title
            if len(first.article.title) < SHORT_TITLE_SIZE
            else f"{first.article.title[:(SHORT_TITLE_SIZE-3)]}..."
        )

        data = DocModel(
            dict(
                doc=dict(
                    oxalink=first.article.oxalink(self._session.site_url),
                    title=escape_latex(first.article.title),
                    short_title=escape_latex(short_title),
                    description=escape_latex(
                        first.article.description if first.article.description else ""
                    ),
                    authors=authors,
                    date=first.article.date,
                    tags=[escape_latex(tag) for tag in first.article.tags],
                ),
                tagged=dict(self._tagged_content),
                options=self._user_options,
            )
        )

        logging.info("Dumping bibtex...")
        bibtex = ""
        if len(self._reference_list) > 0:
            # de-duplicate the bib entries
            bib_entries = list(set(self._reference_list))
            for reference in bib_entries:
                bibtex += str(reference.content) + "\n"

        return data, content, bibtex

    def write(self, allowed_tags: Set[Tag] = None):
        """
        Will write 3 files
         - docmodel.yml
         - context.tex
         - main.bib
        """
        allowed_tags = allowed_tags if allowed_tags is not None else set()
        data, content, bibtex = self.dump(allowed_tags)

        docmodel_filename = os.path.join(self._target_folder, "data.yml")
        with open(docmodel_filename, "w") as file:
            yaml.dump(data, file)
        logging.info("DocModel file created: %s", docmodel_filename)

        content_filename = os.path.join(self._target_folder, "main.tex")
        with open(content_filename, "w") as file:
            for chunk in content:
                file.write(chunk)
                file.write("\n")
        logging.info("Content file created: %s", content_filename)

        bib_filename = os.path.join(self._target_folder, "main.bib")
        with open(bib_filename, "w") as file:
            file.write(bibtex)
        logging.info("Bib file created: %s", bib_filename)

        for tag, content in self._tagged_content.items():
            with open(f"tagged.{tag}.tex", "w") as file:
                file.write(content)
            logging.info("Tagged content file created: tagged.%s.tex", tag)
