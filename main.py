from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_tables
from app.categories.router import router as category_router
from app.operations.router import router as operation_router
from app.analytics.router import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("Включение")
    print("База данных готова к работе")
    yield
    print("Выключение")
    
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index():
    return {"Success": "api created successfully"}


app.include_router(category_router)
app.include_router(operation_router)
app.include_router(analytics_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)