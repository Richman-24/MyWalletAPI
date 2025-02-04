from datetime import date
from typing import List

from sqlalchemy import ForeignKey, Enum, UniqueConstraint
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr

db_url = "sqlite+aiosqlite:///weather.db"
engine = create_async_engine(db_url)
new_session = async_sessionmaker(engine, expire_on_commit=False)

class Model(DeclarativeBase):
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()


class Category(Model):
    __tablename__ = 'categories'
    
    # Добавить ВАЛИДАТОР - category_type in ("income", "expense")

    category_type: Mapped[str] = mapped_column(Enum("income", "expense"), nullable=False)
    operations: Mapped[List["Operation"]] = relationship("Operation", back_populates="category")
    
    __table_args__ = (
        UniqueConstraint('category_type', 'name', name='uq_type_name'),  # Уникальное сочетание
    )

class Operation(Model):
    __tablename__ = 'operations'

    price: Mapped[float] = mapped_column()
    created_at: Mapped[date] = mapped_column()
    description: Mapped[str] = mapped_column()

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id")) 
    category: Mapped[Category] = relationship("Category", back_populates="operations")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)