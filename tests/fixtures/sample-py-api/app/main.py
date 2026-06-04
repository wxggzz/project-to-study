"""Tiny FastAPI app used as a project-to-study test fixture."""
import os

from fastapi import FastAPI

from .models import Item, User  # noqa: F401  (referenced for the fixture)

app = FastAPI()

DATABASE_URL = os.environ["DATABASE_URL"]
API_TOKEN = os.getenv("API_TOKEN")


@app.get("/items")
def list_items():
    return []


@app.post("/items")
def create_item():
    return {}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
