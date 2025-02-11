from enum import Enum
from pydantic import BaseModel


class CategoryType(str, Enum):
    income = "income"
    expense = "expense"


class CreateCategory(BaseModel):
    category_type: CategoryType
    name: str