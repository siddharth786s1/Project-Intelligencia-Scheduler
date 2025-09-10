import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class ScheduledSession(Base):
    __tablename__ = "scheduled_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)  # Usually derived from subject name
    description = Column(Text, nullable=True)
    
    # Core relationships
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=False)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"), nullable=False)
    time_slot_id = Column(UUID(as_uuid=True), ForeignKey("time_slots.id"), nullable=False)
    
    # Session type (e.g., lecture, lab, tutorial)
    session_type = Column(String, nullable=False, default="lecture")
    
    # Duration in minutes (derived from time_slot but can be overridden)
    duration_minutes = Column(Integer, nullable=False)
    
    # Session status
    is_canceled = Column(Boolean, nullable=False, default=False)
    cancellation_reason = Column(String, nullable=True)
    
    # Generation information
    schedule_generation_id = Column(UUID(as_uuid=True), nullable=True)  # ID of the generation run
    soft_constraints_violated = Column(Integer, nullable=False, default=0)  # Count of violated soft constraints
    
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    faculty = relationship("Faculty", back_populates="sessions")
    subject = relationship("Subject", back_populates="sessions")
    batch = relationship("Batch", back_populates="sessions")
    classroom = relationship("Classroom", back_populates="sessions")
    time_slot = relationship("TimeSlot", back_populates="sessions")
    institution = relationship("Institution", back_populates="sessions")
    
    def __str__(self):
        return f"{self.title} - {self.faculty.name} - {self.batch.name}"
