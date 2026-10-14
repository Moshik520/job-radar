from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

JobSource = Literal[
    "greenhouse", "ashby", "lever", "workable", "recruitee", "personio", "rippling", "workday", "comeet"
]


Category = Literal[
    "qa", "fullstack", "frontend", "backend", "mobile", "software", "ai_ml", "data", "devops", "security",
    "hardware", "it_support", "solutions", "product", "design", "ai_training",
    "sales", "marketing", "customer_success", "operations", "finance", "legal", "hr", "admin",
    "mechanical", "trades", "healthcare", "fitness", "education", "general_application", "other",
]


class Job(BaseModel):
    # Python uses snake_case, the JSON sent to Angular uses camelCase (is_israel -> isIsrael).
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    title: str
    company: str
    location: str
    url: str
    source: JobSource
    published_at: str | None
    updated_at: str | None
    is_israel: bool
    category: Category = "other"


class JobsPage(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[Job]
    total: int
    page: int
    page_size: int


class CategoryCount(BaseModel):
    category: Category
    count: int
