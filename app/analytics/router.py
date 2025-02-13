from datetime import date, timedelta
from enum import Enum
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.categories.schemas import CategoryType
from app.database import Category, Operation, new_session
from app.operations.schemas import PeriodEnum

router = APIRouter(prefix="/api/analytics", tags=["Аналитика"])


@router.get("/", description="Выводит статистику по доходам и расходам на период")
async def get_analitics(period: Optional[PeriodEnum] = None):
    async with new_session() as session:
        try:
            if period is None:
                start_date = date.today() - timedelta(days=364)
            else:
                start_date = date.today() - timedelta(days=period.value)

            income_query = select(func.sum(Operation.amount)).where(
                Operation.created_at >= start_date,
                Operation.category.has(category_type="income"),
            )
            expense_query = select(func.sum(Operation.amount)).where(
                Operation.created_at >= start_date,
                Operation.category.has(category_type="expense"),
            )

            income_result = await session.execute(income_query)
            expense_result = await session.execute(expense_query)

            total_income = income_result.scalar() or 0
            total_expenses = expense_result.scalar() or 0
            cashflow = total_income - total_expenses

            return {
                "incomes": total_income,
                "expenses": total_expenses,
                "cashflow": cashflow,
            }

        except Exception as e:
            raise e


@router.get(
    "/categories/", description="Выводит статистику по доходам\расходам на период ПО КАТЕГОРИЯМ"
)
async def get_analitics_by_category(
    types: CategoryType,
    period: Optional[PeriodEnum] = None,
):
    async with new_session() as session:
        try:
            if period is None:
                start_date = date.today() - timedelta(days=364)
            else:
                start_date = date.today() - timedelta(days=period.value)

            subquery = (
                select(
                    Operation.category_id,
                    func.sum(Operation.amount).label("total_amount"),
                )
                .where(
                    Operation.category.has(category_type=types),
                    Operation.created_at >= start_date,
                )
                .group_by(Operation.category_id)
                .subquery()
            )


            query = select(Category.name, subquery.c.total_amount).join(
                subquery, Category.id == subquery.c.category_id
            )

            request = await session.execute(query)
            result = request.all()

            return [{"category": row[0], "total_amount": row[1]} for row in result]

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
