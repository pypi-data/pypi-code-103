import logging
import re
from typing import Dict, List, NewType, Optional, Set, Tuple, Union
from jtex import Tag

from ..client import Session
from ..models import Block, BlockFormat, BlockKind, BlockVersion, Project, User
from .LatexBlockVersion import LatexBlockVersion
from .TaggedContentCollection import TaggedContentCollection
from .utils import LocalMarker, minimise_oxa_path
from .utils.regex import REF_COMMAND_OXA_REGEX


class LatexArticle:
    """
    Class to represent an article in the latex project.
    With the abilty to fetch, localize its assets and write itself to file.
    """

    def __init__(
        self, session: Session, project_id: Union[str, Project], article_id: str
    ):
        self._session: Session = session
        self._project_id: Union[str, Project] = project_id
        self._article_id: str = article_id
        self._block: Optional[Block] = None
        self._version: Optional[BlockVersion] = None
        self._child_blocks: List[Block] = []
        self._child_versions: List[BlockVersion] = []
        self._latex_block_versions: List[LatexBlockVersion] = []
        self._users: List[User] = []

        logging.info("created article")

    @property
    def title(self):
        if self._block:
            return self._block.title
        return ""

    @property
    def description(self):
        if self._block:
            return self._block.description
        return None

    @property
    def authors(self):
        if self._block is None:
            return []
        return self._block.authors if self._block.authors is not None else []

    @property
    def author_names(self):
        names = []
        for author in self.authors:
            if author.user:
                for user in self._users:
                    if user.id == author.user:
                        names.append(user.display_name)
            else:
                names.append(author.plain)
        return names

    @property
    def date(self):
        if self._version:
            return self._version.date or self._version.date_created
        return None

    @property
    def tags(self) -> List[str]:
        if self._block is None:
            return []
        return self._block.tags if self._block.tags is not None else []

    def oxalink(self, base: str):
        if self._version is None:
            return None
        v = self._version
        return f"{base}/oxa:{v.id.project}/{v.id.block}.{v.id.version}"

    def fetch(self, fmt: BlockFormat, version: Optional[int] = None):
        """Download article and all children in Latex format

        Raises ValueError if download fails.
        """
        logging.info("article.fetch")
        block = self._session.get_block(
            self._project_id, self._article_id, kind=BlockKind.article
        )
        logging.info("article.fetch got block")
        version_to_fetch = version or block.latest_version
        children = self._session.get_version_with_children(block, version_to_fetch, fmt)
        if len(children.errors) > 0:
            logging.error("There were errors fetching some children")
            for error in children.errors:
                logging.error(error)

        if children.versions.items[0].kind != BlockKind.article:
            raise ValueError("Expected first child to be an article")
        self._block, *self._child_blocks = children.blocks.items
        self._version, *self._child_versions = children.versions.items
        logging.info(
            f"Processing Article: {self._version.id.project}/"
            f"{self._version.id.block}/versions/{self._version.id.version}"
        )
        logging.info("fetch complete")

    def localize(
        self,
        session: Session,
        assets_folder: str,
        reference_list: List[LocalMarker],
        figure_list: List[LocalMarker],
    ):
        """
            Parse article content, pull assets to local storage and make usable local
            references/labels available to commands as needed

        - images
        - authors
        - citations
        - href
        """
        self._localize_authors(session)
        self._localize_content(session, assets_folder, reference_list, figure_list)

    def reconcile(self):
        """
        For each register figure replace any references found in the content with
        """
        if len(self._latex_block_versions) == 0:
            logging.error("Trying to reconcile article before it was localized")
            return

        for latex in self._latex_block_versions:
            latex.reconcile()

    def _localize_authors(self, session: Session):
        for author in self.authors:
            if author.user is not None:
                try:
                    self._users.append(session.get_user(author.user))
                except ValueError as err:
                    logging.info("Could not get user %s: %s", author.user, err)
                    continue
        logging.info("Localized authors")

    def _localize_content(
        self,
        session: Session,
        assets_folder: str,
        reference_list: List[LocalMarker],
        figure_list: List[LocalMarker],
    ):
        """
        Ignores blocks of any type other than Content and Output.

        @param session: Session to use to get assets
        @param assets_folder: Folder to store assets
        @param reference_list: List of local references
        @param figure_list: List of local figures
        @param tagged_blocks: Set of block tags that should be used to filter special content
        """
        if len(self._child_blocks) == 0:
            logging.warning("Article has no child blocks")
        if len(self._child_versions) == 0:
            logging.warning("Article has no child versions")
        for block, version in zip(self._child_blocks, self._child_versions):
            # pylint: disable=broad-except
            latex = LatexBlockVersion(
                session, assets_folder, reference_list, figure_list, block, version
            )
            try:
                # localizing the block first, even though we may not use the content
                latex.localize()
                self._latex_block_versions.append(latex)
            except Exception as err:
                logging.error("Error localizing block %s: %s", block, err)
                continue
        logging.info("Localized content and references")

    def dump(self, allowed_tags: Set[Tag]) -> Tuple[str, TaggedContentCollection]:
        """
        Dump article to a string, and tagged content collection

        @param tagged_blocks: Set of block tags that should be used to filter special content
        @return: Tuple of (article content, TaggedContentCollection)
        """
        logging.info("Dumping article content")

        content = ""
        tagged_content = TaggedContentCollection()
        content_flow_idx = 0
        allowed_tag_ids = {t.id for t in allowed_tags}
        for latex_block in self._latex_block_versions:
            # pylint: disable=broad-except
            try:
                # handle tagged content
                if "no-export" in set(latex_block.tags):
                    logging.info("Found no-export tag, skipping block")
                    continue

                allowed_and_present_tags = sorted(allowed_tag_ids & set(latex_block.tags))
                if len(allowed_and_present_tags) > 0:
                    for block_tag in allowed_and_present_tags:
                        logging.info("Found tag %s", block_tag)
                        tag_obj = [t for t in list(allowed_tags) if t.id == block_tag][0]
                        if tag_obj.plain:
                            logging.info("Requesting plain text")
                            plain_text = latex_block.fetch_content(BlockFormat.txt)
                            if plain_text is None:
                                break;
                            tagged_content.add(block_tag, plain_text, plain=True)
                        else:
                            logging.info("Using latex content")
                            tagged_content.add(block_tag, latex_block.content)

                    # tagged blocks are removed from normal content flow
                    continue

                # continue on to normal content flow
                if content_flow_idx == 0:
                    content += f"{latex_block.content}\n"
                else:
                    content += f"\n{latex_block.content}\n"
                content_flow_idx += 1
            except Exception as err:
                logging.error("Error dumping block %s: %s", latex_block, err)
                continue

        return content, tagged_content
