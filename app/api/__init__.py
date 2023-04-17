# app/api/__init__.py

from fastapi import APIRouter
from app.api.endpoints import example_router

router = APIRouter()
router.include_router(example_router)