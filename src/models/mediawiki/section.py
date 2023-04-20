import logging
from typing import List, Union

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode
from pydantic import BaseModel

from src.models.exceptions import MissingInformationError
from src.models.wikimedia.wikipedia.reference.generic import WikipediaReference

logger = logging.getLogger(__name__)


class MediawikiSection(BaseModel):
    testing: bool = False
    language_code: str = ""
    wikicode: Union[Wikicode, str]
    references: List[WikipediaReference] = []

    class Config:
        arbitrary_types_allowed = True

    @property
    def __get_lines__(self):
        return str(self.wikicode).split("\n")

    @property
    def name(self):
        """Extracts a section name from the first line of the output from mwparserfromhell"""
        line = self.__get_lines__[0]
        return self.__extract_name_from_line__(line=line)

    @property
    def number_of_references(self):
        return len(self.references)

    @staticmethod
    def star_found_at_line_start(line) -> bool:
        """This determines if the line in the current section has a star"""
        return bool("*" in line[:1])

    def __extract_name_from_line__(self, line):
        from src import app

        app.logger.debug("extract_name_from_line: running")
        return line.replace("=", "")

    def __extract_all_general_references__(self):
        from src import app

        app.logger.debug("__extract_all_general_references__: running")
        # Discard the header line
        lines = str(self.wikicode).split("\n")
        lines_without_heading = lines[1:]
        logger.debug(f"Extracting {len(lines_without_heading)} lines form section {lines[0]}")
        for line in lines_without_heading:
            logger.info(f"Working on line: {line}")
            # Guard against empty line
            # logger.debug("Parsing line")
            # We discard all lines not starting with a star to avoid all
            # categories and other templates not containing any references
            if line and self.star_found_at_line_start(line=line):
                parsed_line = mwparserfromhell.parse(line)
                logger.debug("Appending line with star to references")
                # We don't know what the line contains besides a start
                # but we assume it is a reference
                reference = WikipediaReference(
                    wikicode=parsed_line,
                    # wikibase=self.wikibase,
                    testing=self.testing,
                    language_code=self.language_code,
                    is_general_reference=True,
                    section=self.name,
                )
                reference.extract_and_check()
                self.references.append(reference)

    def __extract_all_footnote_references__(self):
        """This extracts everything inside <ref></ref> tags"""
        from src import app

        app.logger.debug("__extract_all_footnote_references__: running")
        # Thanks to https://github.com/JJMC89,
        # see https://github.com/earwig/mwparserfromhell/discussions/295#discussioncomment-4392452
        # self.__parse_wikitext__()
        if not self.wikicode:
            raise MissingInformationError()
        if self.testing:
            app.logger.info("Testing detected")
            if isinstance(self.wikicode, str):
                app.logger.info("Parsing the test wikitext into wikicode")
                self.wikicode = mwparserfromhell.parse(self.wikicode)
        if isinstance(self.wikicode, Wikicode):
            app.logger.debug("Wikicode detected")
            refs = self.wikicode.filter_tags(
                matches=lambda tag: tag.tag.lower() == "ref"
            )
            app.logger.debug(f"Number of refs found: {len(refs)}")
            for ref in refs:
                reference = WikipediaReference(
                    wikicode=ref,
                    # wikibase=self.wikibase,
                    testing=self.testing,
                    language_code=self.language_code,
                    section=self.name,
                )
                reference.extract_and_check()
                self.references.append(reference)
        else:
            raise MissingInformationError("The section did not have any wikicode")

    def extract(self):
        self.__extract_all_general_references__()
        self.__extract_all_footnote_references__()

