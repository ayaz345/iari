from src.models.api.job.references_job import ReferencesJob
from src.models.api.statistics.references.references_schema import ReferencesSchema
from src.models.file_io.article_file_io import ArticleFileIo
from src.models.file_io.reference_file_io import ReferenceFileIo
from src.views.statistics import StatisticsView


class References(StatisticsView):
    """This returns all references as dehydrated references"""

    job = ReferencesJob  # type: ignore  # (weird error from mypy)
    schema = ReferencesSchema()

    def get(self):
        self.__validate_and_get_job__()
        # load the article json
        articlefileio = ArticleFileIo(wari_id=self.job.wari_id)
        articlefileio.read_from_disk()
        if not articlefileio.data:
            return "No json in cache", 404
        references = articlefileio.data["references"]
        # get the references details
        details = []
        for hash_ in references:
            referencefileio = ReferenceFileIo(hash_based_id=hash_)
            referencefileio.read_from_disk()
            data = referencefileio.data
            if not data:
                return "No json in cache", 404
            # convert to dehydrated reference:
            del data["templates"]
            del data["wikitext"]
            details.append(data)
        data = dict(total=len(references), references=details)
        return data, 200
