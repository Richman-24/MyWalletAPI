from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import new_session, Category


router = APIRouter(
    prefix="/api/categories",
    tags=["Категории"]
)


class CategoryType(str, Enum):
    income = "income"
    expense = "expense"


class CreateCategory(BaseModel):
    category_type: CategoryType
    name: str


@router.get("/", description="Все категории (доходов или расходов)")
async def get_categories(type: CategoryType):
    async with new_session() as session:
        query = select(Category).where(Category.category_type==type)
        response = await session.execute(query)
        categories = response.scalars().all()
        
        return categories


@router.post("/create", description="Создать категорию")
async def create_category(data: Annotated[CreateCategory, Depends()]):
    async with new_session() as session:

        new_data = data.model_dump()
        new_data["name"] = data.name.lower()
        new_category = Category(**new_data)
        
        try:
            session.add(new_category)
            await session.commit() 
            return {"message": "Категория успешно создана", "category": new_category.name.title()}
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=400, detail=f"Категория с таким именем уже существует")
        






# @router.post("/categories/create_test", description="Создать категорию test")
# async def create_category(name: str, type: str):
#     async with new_session() as session:        
#         new_category = Category(name=name, category_type=type)
        
#         try:
#             session.add(new_category)
#             await session.commit() 
#             return {"message": "Категория успешно создана", "category": new_category.name}
#         except IntegrityError:
#             await session.rollback()
#             raise HTTPException(status_code=400, detail=f"Категория с таким именем уже существует")


# # @router.post("categories/name/") - работает.
# async def get_category_by_name(data: Annotated[CreateCategory, Depends()]):
#     async with new_session() as session:
#         new_data = data.model_dump()
#         query = select(Category).where(
#             Category.category_type == new_data["category_type"],
#             Category.name == new_data["name"])
        
#         result = await session.execute(query)
#         category = result.scalars().first()
        
#         if category is not None:
#             return category
#         else:
#             raise HTTPException(status_code=404, detail="Категория не найдена")