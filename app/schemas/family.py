from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FamilyMemberCreate(BaseModel):
    name: str
    relation: str


class FamilyMemberOut(BaseModel):
    id: int
    name: str
    relation: str
    photo_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
