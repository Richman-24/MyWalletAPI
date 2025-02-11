from datetime import date, timedelta
from enum import Enum
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import Category, new_session, Operation
from app.categories.router import CategoryType


router = APIRouter(
    prefix="/api/analytics",
    tags=["Аналитика"]
)

