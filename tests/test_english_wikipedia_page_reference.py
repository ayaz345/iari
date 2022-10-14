import logging
from unittest import TestCase

import config
from src import console
from src.models.exceptions import MissingInformationError, MoreThanOneNumberError
from src.models.return_.wikibase_return import WikibaseReturn
from src.models.wikibase.ia_sandbox_wikibase import IASandboxWikibase
from src.models.wikimedia.wikipedia.reference.english.english_reference import EnglishWikipediaReference
from src.models.wikimedia.wikipedia.reference.english.google_books import GoogleBooks
from src.models.wikimedia.wikipedia.reference.english.schema import (
    EnglishWikipediaReferenceSchema,
)

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class TestEnglishWikipediaReferenceSchema(TestCase):
    def test_url_template1(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
        }

        reference = EnglishWikipediaReferenceSchema().load(data)
        console.print(reference)

    def test_url_template_with_archive_url(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
            "archive_url": "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
        }

        reference = EnglishWikipediaReferenceSchema().load(data)
        assert (
            reference.archive_url
            == "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php"
        )
        # console.print(reference)

    def test_url_template2(self):
        data = {"1": "chkchkchk.net", "template_name": "url"}
        reference = EnglishWikipediaReferenceSchema().load(data)
        console.print(reference)

    def test_parse_persons_from_cite_web(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
        }

        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        console.print(reference)
        person = reference.persons_without_role[0]
        assert person.given == "Melissa"
        assert person.surname == "Locker"

    def test_parse_persons_from_cite_journal(self):
        data = {
            "last1": "Skaaning",
            "first1": "Svend-Erik",
            "title": "Different Types of Data and the Validity of Democracy Measures",
            "journal": "Politics and Governance",
            "volume": "6",
            "issue": "1",
            "page": "105",
            "doi": "10.17645/pag.v6i1.1183",
            "year": "2018",
            "doi_access": "free",
            "template_name": "cite journal",
        }
        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        console.print(reference)
        person = reference.persons_without_role[0]
        assert person.given == "Svend-Erik"
        assert person.surname == "Skaaning"

    def test_parse_persons_from_cite_book(self):
        data = {
            "last": "Tangian",
            "first": "Andranik",
            "date": "2020",
            "title": "Analytical Theory of Democracy: History, Mathematics and Applications",
            "series": "Studies in Choice and Welfare",
            "publisher": "Springer",
            "location": "Cham, Switzerland",
            "isbn": "978-3-030-39690-9",
            "doi": "10.1007/978-3-030-39691-6",
            "s2cid": "216190330",
            "template_name": "cite book",
        }
        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        console.print(reference)
        person = reference.persons_without_role[0]
        assert person.given == "Andranik"
        assert person.surname == "Tangian"

    def test_extract_first_level_domain(self):
        data = {
            "url": "https://www.stereogum.com/1345401/turntable-interview/interviews/",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
            "archive_url": "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
        }
        reference = EnglishWikipediaReferenceSchema().load(data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        assert reference.first_level_domain_of_url == "stereogum.com"
        assert (
            reference.url
            == "https://www.stereogum.com/1345401/turntable-interview/interviews/"
        )

    def test_extract_first_level_domain_bad_url(self):
        data = {
            "url": "[[:sq:Shkrime për historinë e Shqipërisë|Shkrime për historinë e Shqipërisë]]",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
            "archive_url": "https://web.archive.org/web/20100715195638/http://www.ine.cl/canales/chile_estadistico/censos_poblacion_vivienda/censo_pobl_vivi.php",
        }
        reference = EnglishWikipediaReferenceSchema().load(data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        assert reference.url is None

    def test_find_number(self):
        ref = EnglishWikipediaReference(
            template_name="test",
            wikibase=IASandboxWikibase(),
        )
        with self.assertRaises(MoreThanOneNumberError):
            ref.__find_number__(string="123one123")
        assert ref.__find_number__(string="1one") == 1
        assert ref.__find_number__(string="one1one") == 1
        assert ref.__find_number__(string="one") is None

    def test_publisher_and_location(self):
        data = dict(
            template_name="cite web",
            url="http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
            archive_url="https://web.archive.org/web/20100812051822/http://www.kmk.a.se/ImageUpload/kmkNytt0110.pdf",
            url_status="dead",
            archive_date="2010-08-12",
            title="Musköbasen 40 år",
            first="Helene",
            last="Skoglund",
            author2="Nynäshamns Posten",
            date="January 2010",
            publisher="Kungliga Motorbåt Klubben",
            location="Stockholm",
            pages="4–7",
            language="Swedish",
            trans_title="Muskö Naval Base 40 years",
            access_date="2010-11-09",
        )
        reference = EnglishWikipediaReferenceSchema().load(data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        assert reference.publisher == "Kungliga Motorbåt Klubben"
        assert reference.location == "Stockholm"

    def test_detect_archive_urls(self):
        # TODO test other archives also
        from src.models.wikibase.enums import KnownArchiveUrl

        reference = EnglishWikipediaReference(
            wikibase=IASandboxWikibase(),
            archive_url="https://web.archive.org/web/20190701062212/http://www.mgtrust.org/ind1.htm",
            template_name="test",
        )
        reference.finish_parsing_and_generate_hash()
        # logger.debug(reference.detected_archive_of_url)
        # logger.debug(reference.detected_archive_of_archive_url)
        assert reference.detected_archive_of_url is None
        assert reference.detected_archive_of_archive_url == KnownArchiveUrl.ARCHIVE_ORG

    def test_google_books(self):
        data = {
            "url": "{{google books |plainurl=y |id=CDJpAAAAMAAJ |page=313}}",
            "title": "Turntable Interview: !!!",
            "last": "Locker",
            "first": "Melissa",
            "date": "May 9, 2013",
            "website": "Stereogum",
            "access_date": "May 24, 2021",
            "template_name": "cite web",
        }
        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        # console.print(type(reference.google_books))
        assert reference.first_level_domain_of_url == "google.com"
        self.assertIsInstance(reference.google_books, GoogleBooks)

    def test_detect_internet_archive_id(self):
        data = dict(
            url="https://archive.org/details/catalogueofshipw0000wils/",
            template_name="cite book",
        )
        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        # print(reference.internet_archive_id)
        assert reference.internet_archive_id == "catalogueofshipw0000wils"

    def test_detect_google_books_id(self):
        data = dict(
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        # print(reference.internet_archive_id)
        assert reference.google_books_id == "on0TaPqFXbcC"

    def test_clean_wiki_markup_from_strings(self):
        data = dict(
            publisher="[[test]]",
            template_name="cite book",
        )
        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        # print(reference.internet_archive_id)
        assert reference.publisher == "test"
        data = dict(
            # publisher="",
            template_name="cite book",
        )
        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        # print(reference.internet_archive_id)
        assert reference.publisher is None

    def test_clean_wiki_markup_from_strings_complicated_markup(self):
        data = dict(
            publisher="[[test|test]]",
            template_name="cite book",
        )
        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        assert reference.publisher == "test"

    def test_handle_place(self):
        data = dict(
            place="Copenhagen",
            template_name="cite book",
        )
        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        assert reference.location == "Copenhagen"

    def test_handle_lang(self):
        data = dict(
            lang="English",
            template_name="cite book",
        )
        reference: EnglishWikipediaReference = EnglishWikipediaReferenceSchema().load(
            data
        )
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        assert reference.language == "English"

    def test_periodical(self):
        data = dict(
            template_name="cite web",
            periodical="test",
        )
        reference = EnglishWikipediaReferenceSchema().load(data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        assert reference.periodical == "test"

    def test_oclc(self):
        data = dict(
            oclc="test",
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        assert reference.oclc == "test"

    def test_has_first_level_domain_url_hash_and_has_hash(self):
        data = dict(
            oclc="test",
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        assert reference.has_first_level_domain_url_hash is False
        assert reference.has_hash is False
        reference.wikibase = IASandboxWikibase()
        reference.finish_parsing_and_generate_hash()
        assert reference.has_first_level_domain_url_hash is True
        assert reference.has_hash is True

    def test_template_url(self):
        data = dict(
            oclc="test",
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        assert (
            reference.template_url
            == f"https://en.wikipedia.org/wiki/Template:cite book"
        )

    def test_wikibase_url(self):
        data = dict(
            oclc="test",
            url="https://books.google.ca/books?id=on0TaPqFXbcC&pg=PA431",
            template_name="cite book",
        )
        reference = EnglishWikipediaReference(**data)
        reference.wikibase = IASandboxWikibase()
        with self.assertRaises(MissingInformationError):
            print(reference.wikibase_url)
        reference.return_ = WikibaseReturn(item_qid="test", uploaded_now=False)
        # print(reference.wikibase_url)
        assert (
            reference.wikibase_url
            == f"https://ia-sandbox.wikibase.cloud/wiki/Item:test"
        )
