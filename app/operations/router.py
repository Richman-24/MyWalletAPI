from datetime import date, timedelta
from enum import Enum
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import Category, new_session, Operation
from app.categories.router import CategoryType


router = APIRouter(
    prefix="/api/operations",
    tags=["Операции"]
)

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

    
@router.post("/create/")
async def create_operation(data: Annotated[OperationCreate, Depends()]) -> dict:
    async with new_session() as session:
        new_data = data.model_dump()
        new_operation = Operation(**new_data)

        try:
            session.add(new_operation)
            await session.commit() 
            return {"message": "Операция успешно записана"}
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=e)

@router.get("/")
async def get_operations(data: Annotated[OperationGet, Depends()]):
    async with new_session() as session:
        if data.period is None:
            start_date = date.today()
        else:
            start_date = date.today() - timedelta(days=data.period.value)

        query = select(Operation).join(Category).where(
            Category.category_type == data.type,
            Operation.created_at >= start_date
        )
        response = await session.execute(query)
        result = response.scalars().all()

        if result:
            return result
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Операций не найдено"
        )

@router.get("/all/")
async def get_all_operations(period: Optional[PeriodEnum] = None):
    async with new_session() as session:
        if period is None:
            start_date = date.today()
        else:
            start_date = date.today() - timedelta(days=period.value)

        query = (
        select(Operation)
        .options(selectinload(Operation.category))  # Загрузка связанных категорий #ЗАПОМНИТЬ
        .where(Operation.created_at >= start_date)
    )

        response = await session.execute(query)
        result = response.scalars().all()
        
        if result:
            # new_res = []

            # for item in result:
            #     typ = item.category.category_type == "income"
            #     if typ: 
            #         new_res.append(f"+{item.amount}")
            #     else:
            #         new_res.append(f"-{item.amount}")
            # return new_res
            return result
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Операций не найдено")