from typing import List

from fastapi import FastAPI
import sqlalchemy
import databases
from pydantic import BaseModel
from sqlalchemy.sql.functions import user

from routers import foos, users
from src.models import HelloWorldModel, GetItemModel, ItemInput

app = FastAPI()
app.include_router(foos.router)
app.include_router(users.router)

# SQLAlchemy specific code, as with any other app
DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("completed", sqlalchemy.Boolean),
)
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


class NoteInput(BaseModel):
    text: str
    completed: bool


class Note(BaseModel):
    id: int
    text: str
    completed: bool



@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root() -> HelloWorldModel:
    return HelloWorldModel(message="Hello World")


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> GetItemModel:
    return GetItemModel(item_id=item_id)


@app.post("/items/")
async def create_item(item: ItemInput) -> ItemInput:
    return item


@app.get("/notes/", response_model=List[Note])
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)


@app.post("/notes/", response_model=Note)
async def create_note(note: NoteInput):
    query = notes.insert().values(text=note.text, completed=note.completed)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}
