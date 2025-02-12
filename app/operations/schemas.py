from enum import Enum
from typing import Optional
from pydantic import BaseModel

from app.categories.schemas import CategoryType


class OperationCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    category_id: int


class PeriodEnum(int, Enum):
    DAY = 1
    WEEK = 7
    MONTH = 31


class OperationGet(BaseModel):
    type: CategoryType
    period: Optional[PeriodEnum] = None
