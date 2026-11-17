from typing import TypeVar, Generic
from pydantic import BaseModel

# 定义一个通用泛型
T = TypeVar("T")
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PageResult(BaseModel, Generic[T]):
    """通用分页结果"""

    items: list[T]
    page: int
    page_size: int
    total: int