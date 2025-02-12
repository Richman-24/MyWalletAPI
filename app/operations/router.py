from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.operations.repository import OperationsRepo
from app.operations.schemas import OperationCreate, OperationGet, PeriodEnum


router = APIRouter(
    prefix="/api/operations",
    tags=["Операции"]
)

# List (by type for period) 
@router.get("/", description="Список доходов \ расходов за период N")
async def get_operations(data: Annotated[OperationGet, Depends()]):
    # Вывод операций ( только доходов \ расходов) за период 1\7\31\365
    try:
        operations = await OperationsRepo.get_operations(data)
        return operations
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e.detail))


# List (for the period)
@router.get("/all/", description="Общий список операций за период N")
async def get_all_operations(period: Optional[PeriodEnum] = None):
    # Вывод ВСЕХ операций за период 1\7\31\365
    try:
        operations = await OperationsRepo.get_all(period.value if period else None)
        return operations
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e.detail))


# Create one
@router.post("/create/", description="Создать запись")
async def create_operation(data: Annotated[OperationCreate, Depends()]) -> dict:
    try:
        new_op = await OperationsRepo.create_one(data)
        return {"message": "Операция успешно записана", "id": new_op.id}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e.detail))

# Retrive one
@router.get("/{operation_id}/", description="Просмотреть запись по id")
async def get_operation(operation_id: str):
    try:
        op_data = await OperationsRepo.get_one_operation(operation_id)
        return op_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Update one
@router.patch("/{operation_id}/edit/", description="Изменить запись")
async def update_operation(
    operation_id: str, data: Annotated[OperationCreate, Depends()]):
    try: 
        upd_operation = await OperationsRepo.update_operation(operation_id, data)
        return {"message": "Запись успешно изменена:", "id": str(upd_operation)}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e.detail))

# Delete one
@router.delete("/{operation_id}/delete/", description="Удалить запись")
async def delete_operation(operation_id: str):
    try:
        await OperationsRepo.delete_one(operation_id)
        return {"message": "Запись успешно удалена"}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
