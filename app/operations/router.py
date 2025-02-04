from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

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

@router.get("/{type}")
async def get_operations_by_category_type(type: CategoryType):
    async with new_session() as session:
        query = select(Operation).join(Category).where(Category.category_type == type)
        response = await session.execute(query)
        result = response.scalars().all()

        if result is not None and len(result) > 0:
            return result
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Операций не найдено"
        )

