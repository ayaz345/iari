from src.models.api.job.article_job import ArticleJob
from src.models.api.statistics.all import AllHandler
from src.models.api.statistics.article.article_schema import ArticleSchema
from src.views.statistics import StatisticsView


class All(StatisticsView):
    """This models the get-statistics API
    It is instantiated at every request"""

    schema = ArticleSchema()
    job: ArticleJob

    def get(self):
        self.__validate_and_get_job__()
        handler = AllHandler(job=self.job)
        handler.fetch_and_compile()
        return handler.compilation, 200
