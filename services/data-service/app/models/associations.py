import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Table
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base

# Association table for batch-subject many-to-many relationship
batch_subject = Table(
    "batch_subjects",
    Base.metadata,
    Column("batch_id", UUID(as_uuid=True), ForeignKey("batches.id"), primary_key=True),
    Column("subject_id", UUID(as_uuid=True), ForeignKey("subjects.id"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)
