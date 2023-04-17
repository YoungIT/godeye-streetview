# app/api/endpoints.py

from fastapi import APIRouter

example_router = APIRouter()

@example_router.get("/example")
def example_endpoint():
    return {"message": "Hello, World!"}