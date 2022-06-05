from fastapi import FastAPI

from models import HelloWorldModel, GetItemModel, ItemInput
from routers import foos, users, notes

app = FastAPI()
app.include_router(foos.router)
app.include_router(users.router)
app.include_router(notes.router)


@app.get("/")
async def root() -> HelloWorldModel:
    return HelloWorldModel(message="Hello World")


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> GetItemModel:
    return GetItemModel(item_id=item_id)


@app.post("/items/")
async def create_item(item: ItemInput) -> ItemInput:
    return item
