from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

JobSource = Literal["greenhouse", "lever", "ashby", "workday", "comeet"]


class Job(BaseModel):
    # Python uses snake_case, the JSON sent to Angular uses camelCase (is_israel -> isIsrael).
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    title: str
    company: str
    location: str
    url: str
    source: JobSource
    published_at: str
    updated_at: str
    is_israel: bool


class JobsPage(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[Job]
    total: int
    page: int
    page_size: int
