import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID

import databases
import sqlalchemy
from eventsourcing.application import Application
from eventsourcing.domain import event
from eventsourcing.persistence import Mapper, Transcoder
from fastapi import APIRouter
from pydantic import BaseModel

from routers.infrastructure import Snapshot, Aggregate, PydanticMapper, OrjsonTranscoder

router = APIRouter()
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
    id: uuid.UUID
    text: Optional[str]
    completed: bool


class NoteAggregate(Aggregate):
    class Registered(Aggregate.Created):
        type: str

    @event(Registered)
    def __init__(self, type):
        self.type = type
        self.text = None

    class TextUpdated(Aggregate.Event):
        text: str

    @event(TextUpdated)
    def set_text(self, text):
        self.text = text


class NoteCommandHandler(Application):
    is_snapshotting_enabled = True
    snapshot_class = Snapshot

    def register_note(self, type, text):
        note = NoteAggregate(type)
        note.set_text(text)
        self.save(note)
        return note.id

    def update_note(self, note_id, text):
        note = self.repository.get(note_id)
        note.set_text(text)
        self.save(note)

    def get_note(self, note_id):
        note = self.repository.get(note_id)
        return note

    def construct_mapper(self) -> Mapper:
        return self.factory.mapper(
            transcoder=self.construct_transcoder(),
            mapper_class=PydanticMapper,
        )

    def construct_transcoder(self) -> Transcoder:
        return OrjsonTranscoder()


@router.on_event("startup")
async def startup():
    import os

    # Use SQLite for persistence.
    os.environ['PERSISTENCE_MODULE'] = 'eventsourcing.sqlite'

    # Configure SQLite database URI. Either use a file-based DB;
    os.environ['SQLITE_DBNAME'] = 'sqlite-db'

    # Set optional lock timeout (default 5s).
    os.environ['SQLITE_LOCK_TIMEOUT'] = '10'  # seconds

    await database.connect()


@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@router.get("/notes/", response_model=List[Note])
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)


@router.post("/notes/", response_model=Note)
async def create_note(note: NoteInput):
    query = notes.insert().values(text=note.text, completed=note.completed)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}


@router.post("/noteses/")
async def create_note_es(note: NoteInput):
    application = NoteCommandHandler()
    note_id = application.register_note("customnote", note.text)
    return {"id": note_id}


@router.post("/noteses/{note_id}")
async def update_note_es(note_id: UUID, note: NoteInput):
    application = NoteCommandHandler()
    note_id = application.update_note(note_id, note.text)
    return {"id": note_id}


@router.get("/noteses/{note_id}", response_model=Note)
async def get_note_es(note_id: UUID):
    application = NoteCommandHandler()
    note = application.get_note(note_id)
    return Note(id=note.id, text=note.text, completed=True)
