import logging
import re
from typing import Dict, List

import mwparserfromhell  # type: ignore
from mwparserfromhell.wikicode import Wikicode  # type: ignore

from src.models.api.job.article_job import ArticleJob
from src.models.base import WariBaseModel
from src.models.exceptions import MissingInformationError
from src.models.mediawiki.section import MediawikiSection
from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference
from src.models.wikimedia.wikipedia.url import WikipediaUrl

# logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class WikipediaReferenceExtractor(WariBaseModel):
    """This class handles all extraction of references from wikicode

    Design:
    * first we get the wikicode
    * we parse it with mwparser from hell
    * we extract the raw references -> WikipediaReference
    """

    job: ArticleJob
    wikitext: str
    wikicode: Wikicode = None
    references: List[WikipediaReference] = []
    # wikibase: Wikibase
    testing: bool = False
    check_urls: bool = False
    check_urls_done: bool = False
    checked_and_unique_reference_urls: List[WikipediaUrl] = []
    language_code: str = ""
    sections: List[MediawikiSection] = []

    class Config:  # dead: disable
        arbitrary_types_allowed = True  # dead: disable

    @property
    def urls(self) -> List[WikipediaUrl]:
        """List of non-unique urls"""
        urls: List[WikipediaUrl] = list()
        for reference in self.references:
            for url in reference.reference_urls:
                urls.append(url)
        return urls

    @property
    def raw_urls(self) -> List[str]:
        """List of raw non-unique urls found in the reference"""
        urls: List[str] = list()
        for reference in self.references:
            for url in reference.reference_urls:
                urls.append(url.url)
        return urls

    @property
    def reference_first_level_domain_counts(self) -> Dict[str, int]:
        """This returns a dict with fld as key and the count as value"""
        fld_set = set(self.reference_first_level_domains)
        counts = dict()
        for fld in fld_set:
            count = self.reference_first_level_domains.count(fld)
            counts[fld] = count
        # Sort by count, descending
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        # Thanks to Sawood for recommending we simplify and return a dictionary
        sorted_counts_dictionary = {}
        for element in sorted_counts:
            fld = str(element[0])
            count = int(element[1])
            sorted_counts_dictionary[fld] = count
        return sorted_counts_dictionary

    @property
    def reference_first_level_domains(self) -> List[str]:
        """This is a list and duplicates are likely and wanted"""
        if not self.content_references:
            return []
        flds = []
        for reference in self.content_references:
            if not reference.first_level_domains_done:
                reference.__extract_first_level_domains__()
            for fld in reference.first_level_domains:
                flds.append(fld)
        return flds

    @property
    def number_of_sections_found(self) -> int:
        if not self.sections:
            self.__extract_sections__()
        return len(self.sections)

    @property
    def general_references(self):
        return [
            reference
            for reference in self.content_references
            if reference.is_general_reference
        ]

    @property
    def number_of_general_references(self) -> int:
        return len(self.general_references)

    @property
    def footnote_references(self):
        return [
            reference
            for reference in self.content_references
            if reference.is_footnote_reference
        ]

    @property
    def number_of_footnote_references(self) -> int:
        return len(self.footnote_references)

    @property
    def empty_named_references(self):
        """Special type of reference with no content
        Example: <ref name="INE"/>"""
        return [
            reference
            for reference in self.references
            if reference.is_empty_named_reference
        ]

    @property
    def number_of_empty_named_references(self) -> int:
        return len(self.empty_named_references)

    @property
    def content_references(self):
        """This is references with actual content beyond a name"""
        return [
            reference
            for reference in self.references
            if not reference.is_empty_named_reference
        ]

    @property
    def number_of_content_references(self) -> int:
        return len(self.content_references)

    @property
    def number_of_references(self) -> int:
        return len(self.references)

    # def number_of_content_references_with_a_url(
    #     self, list_: List[WikipediaReference]
    # ) -> int:
    #     if not list_:
    #         list_ = self.content_references
    #     result = len([ref for ref in list_ if ref and ref.url_found])
    #     return result
    #

    def __extract_all_raw_general_references__(self):
        """This extracts everything inside <ref></ref> tags"""
        from src import app

        app.logger.debug("__extract_all_raw_general_references__: running")
        # Thanks to https://github.com/JJMC89,
        # see https://github.com/earwig/mwparserfromhell/discussions/295#discussioncomment-4392452
        self.__extract_sections__()

    def extract_all_references(self):
        """Extract all references from self.wikitext"""
        from src import app

        app.logger.debug("extract_all_references: running")
        if not self.job:
            raise MissingInformationError("no job")
        self.__parse_wikitext__()
        self.__extract_sections__()
        app.logger.info("Done extracting all references")

    def __extract_sections__(self) -> None:
        """This uses the regex supplied by the patron via the API
        and populate the reference_sections attribute with a list of MediawikiSection objects"""
        from src import app

        app.logger.debug("__extract_sections__: running")
        if not self.wikicode:
            self.__parse_wikitext__()
        sections: List[Wikicode] = self.wikicode.get_sections(
            levels=[2],
            matches=self.job.regex,
            flags=re.I,
            include_headings=True,
        )
        """turn mwparserfromhell sections into MediawikiSections"""
        for section in sections:
            mw_section = MediawikiSection(
                wikicode=section, testing=self.testing, language_code=self.language_code
            )
            mw_section.extract()
            self.sections.append(mw_section)
        app.logger.debug(f"Number of sections found: {len(self.sections)}")

    def __parse_wikitext__(self):
        from src import app

        app.logger.debug("__parse_wikitext__: running")
        if not self.wikicode:
            self.wikicode = mwparserfromhell.parse(self.wikitext)

    @property
    def reference_ids(self) -> List[str]:
        ids = []
        for reference in self.references:
            ids.append(reference.reference_id)
        return ids
