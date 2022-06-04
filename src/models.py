"""
I always like to return strongly typed responses whenever possible
"""
from typing import Optional
from pydantic import BaseModel


class HelloWorldModel(BaseModel):
    message: str


class GetItemModel(BaseModel):
    item_id: str


class ItemInput(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
