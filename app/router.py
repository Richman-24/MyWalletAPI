from fastapi import APIRouter
from sqlalchemy import select

from app.database import new_session, IncomeCategory

router = APIRouter(
    prefix="/api",
    tags=["Доходы"]
)


@router.get("/categories/income/")
async def get_categories():
    async with new_session() as session:
        query = select(IncomeCategory)
        response = await session.execute(query)
        categories = response.scalars().all()
        
        return categories