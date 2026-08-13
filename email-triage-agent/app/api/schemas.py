from datetime import datetime, date
from pydantic import BaseModel
from app.db.models import EmailCategory


class EmailResponse(BaseModel):
    id: int
    gmail_message_id: str
    sender: str
    subject: str | None
    received_at: datetime | None
    category: EmailCategory
    summary: str | None
    due_date: date | None
    first_seen_unread_at: datetime | None
    moved_to_pending: bool

    class Config:
        from_attributes = True  # permite crear este schema directo desde un objeto SQLAlchemy


class SyncTriggerResponse(BaseModel):
    message: str
    task_id: str