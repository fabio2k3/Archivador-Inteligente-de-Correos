import enum
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Enum
from sqlalchemy.sql import func
from app.db.session import Base


class EmailCategory(str, enum.Enum):
    IMPORTANTE = "importante"
    NEWSLETTER = "newsletter"
    SPAM = "spam"
    SIN_CLASIFICAR = "sin_clasificar"


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    gmail_message_id = Column(String, unique=True, index=True, nullable=False)
    gmail_thread_id = Column(String, index=True)

    sender = Column(String, nullable=False)
    subject = Column(String)
    received_at = Column(DateTime(timezone=True))

    category = Column(Enum(EmailCategory), default=EmailCategory.SIN_CLASIFICAR)

    summary = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)

    first_seen_unread_at = Column(DateTime(timezone=True), nullable=True)
    moved_to_pending = Column(Boolean, default=False)
    processed_by_ai = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())