from datetime import date
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr

db_url = "sqlite+aiosqlite:///weather.db"
engine = create_async_engine(db_url)
new_session = async_sessionmaker(engine, expire_on_commit=False)

class Model(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

class IncomeCategory(Model):
    incomes: Mapped[list["Income"]] = relationship("Income", back_populates="category")

class ExpenseCategory(Model):
    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="category")

class Operation(Model): 
    name: Mapped[str] = mapped_column(unique=False)
    price: Mapped[float]
    date: Mapped[date]
    description: Mapped[str]  # Исправлено: descripiption на description
    
    __abstract__ = True

class Income(Operation):
    category_id: Mapped[int] = mapped_column(ForeignKey("incomecategorys.id"))
    category: Mapped[IncomeCategory] = relationship("IncomeCategory", back_populates="incomes")

class Expense(Operation):
    category_id: Mapped[int] = mapped_column(ForeignKey("expensecategorys.id"))
    category: Mapped[ExpenseCategory] = relationship("ExpenseCategory", back_populates="expenses")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)