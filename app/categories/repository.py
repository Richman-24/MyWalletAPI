from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.categories.schemas import CreateCategory
from app.database import Category, new_session



class CategoryRepo:

    @classmethod
    async def create_one(cls, data: Annotated[CreateCategory, Depends()]):
        async with new_session() as session:

            new_data = data.model_dump()
            new_data["name"] = data.name.lower()
            new_category = Category(**new_data)
            
            try:
                session.add(new_category)
                await session.commit() 
                await session.flush()
                
                return new_category.id
            
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=400, detail=f"Категория с таким именем уже существует")
    
    @classmethod
    async def get_one(cls, category_id: int):
        async with new_session() as session:
            try:
                query = select(Category).where(Category.id == category_id)
                response = await session.execute(query)
                result = response.scalar_one()

            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Категория с таким id не существует")
            return result
    
    @classmethod
    async def get_all(cls):
        async with new_session() as session:
            query = select(Category)
            response = await session.execute(query)
            categories = response.scalars().all()
            
            return categories
        
    @classmethod
    async def update_one(
        cls,
        category_id: int,
        data: Annotated[CreateCategory, Depends()]
    ):
        async with new_session() as session:
            try:
                new_data = data.model_dump()
                category_instance = await cls.get_one(category_id)
                category_instance.category_type = new_data["category_type"]
                category_instance.name = new_data["name"]
            
                session.add(category_instance)
                await session.commit()
                await session.flush()

                return category_instance.id
            
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=400, detail=f"Категория с таким именем уже существует")

    @classmethod
    async def delete_one(cls, category_id: int):
        async with new_session() as session:
            try:
                category_instance = await cls.get_one(category_id)

                await session.delete(category_instance)
                await session.commit()

            except IntegrityError:
                raise HTTPException(status_code=400, detail=f"В этой категории есть записи")

            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Категория не найдена")