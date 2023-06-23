from marshmallow import post_load
from marshmallow.fields import Int, String

from src.models.api.job.check_doi_job import CheckDoiJob
from src.models.api.schema.refresh import BaseSchema


class CheckDoiSchema(BaseSchema):
    """This validates the patron input in the get request"""

    doi = String()
    timeout = Int()

    # noinspection PyUnusedLocal
    @post_load
    def return_object(self, data, **kwargs) -> CheckDoiJob:    # type: ignore # dead: disable
        """Return job object"""
        from src import app

        app.logger.debug("return_object: running")
        return CheckDoiJob(**data)
