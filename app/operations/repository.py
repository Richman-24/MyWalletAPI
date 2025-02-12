from datetime import date, timedelta
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.operations.schemas import OperationCreate, OperationGet
from app.database import Category, Operation, new_session


class OperationsRepo:
    @classmethod
    async def get_operations(cls, data: Annotated[OperationGet, Depends()]):
    # Вывод операций ( только доходов \ расходов) за период 1\7\31\365
        async with new_session() as session:
            if data.period is None:
                start_date = date.today() - timedelta(days=364)
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

    @classmethod
    async def get_all(cls, period: Optional[int]):
        async with new_session() as session:
            if period is None:
                start_date = date.today() - timedelta(days=364)
            else:
                start_date = date.today() - timedelta(days=period)

            query = (
            select(Operation)
            .options(selectinload(Operation.category))  # Загрузка связанных категорий #ЗАПОМНИТЬ
            .where(Operation.created_at >= start_date)
        )

            response = await session.execute(query)
            result = response.scalars().all()
            
            if result:
                return result
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Операций не найдено")

        
    @classmethod
    async def create_one(cls, data: Annotated[OperationCreate, Depends()]) -> int:
        async with new_session() as session:
            new_data = data.model_dump()
            new_operation = Operation(**new_data)

            try:
                session.add(new_operation)
                await session.commit()
                await session.flush()
                return new_operation

            except Exception as e:
                raise e
    
    @classmethod
    async def get_one_operation(cls, operation_id: int):
        async with new_session() as session:
            try:
                query = select(Operation).where(Operation.id == operation_id)
                response = await session.execute(query)
                result = response.scalar_one()

                return result
            
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Операция не найдена")

    @classmethod
    async def update_operation(
        cls,
        operation_id: int,
        data: Annotated[OperationCreate, Depends()]
        ) -> int:
        async with new_session() as session:
            try:
                new_data = data.model_dump()
                operation_instance = await cls.get_one_operation(operation_id)
                
                operation_instance.category_id = new_data["category_id"]
                operation_instance.description = new_data["description"]
                operation_instance.amount = new_data["amount"]
                
                session.add(operation_instance)
                await session.commit()
                await session.flush()
                return operation_instance
            
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=400, detail=f"Запись не найдена")
                #raise e

    @classmethod
    async def delete_one(cls, operation_id: int):
        async with new_session() as session:
            try:
                operation_instance = await cls.get_one_operation(operation_id)

                await session.delete(operation_instance)
                await session.commit()

            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Запись не найдена")