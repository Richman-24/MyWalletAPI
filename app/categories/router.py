from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.categories.repository import CategoryRepo
from app.categories.schemas import CategoryType, CreateCategory
from app.database import new_session, Category


router = APIRouter(
    prefix="/api/categories",
    tags=["Категории"]
)

# List (by_type)
@router.get("/", description="Все категории (доходов или расходов)")
async def get_categories_by_type(type: CategoryType):
    async with new_session() as session:
        query = select(Category).where(Category.category_type == type)
        response = await session.execute(query)
        result = response.scalars().all()

        if result is not None and len(result) > 0:
            return result
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категорий не добавлено"
        )

# List (all)
@router.get("/all/", description="Вывести вообще все категории")
async def get_all_category():
    categories = await CategoryRepo.get_all()
    
    if categories is not None and len(categories) > 0:
        return categories
    
    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категорий не добавлено"
        )

# Create
@router.post("/create/", description="Создать категорию")
async def create_category(data: Annotated[CreateCategory, Depends()]) -> dict[str, str]:
        try:
            new_category = await CategoryRepo.create_one(data)
            return {"message": "Категория успешно создана:", "id": str(new_category)}

        except Exception as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

# Retrieve
@router.get("/{category_id}")
async def get_one_category(category_id: str):
    try:
        category_data = await CategoryRepo.get_one(category_id)
        return category_data

    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# Update
@router.post("/{category_id}/edit")
async def update_category(
    category_id: str,
    data: Annotated[CreateCategory, Depends()])  -> dict[str, str]:
    
    try:
        updated_category = await CategoryRepo.update_one(category_id, data) 
        return {"message": "Категория успешно изменена:", "id": str(updated_category)}

    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# Delete
@router.delete("/{category_id}/delete")
async def delete_category(category_id: str):
    try:
        await CategoryRepo.delete_one(category_id)
        return {"message": "Категория успешно удалена"}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
