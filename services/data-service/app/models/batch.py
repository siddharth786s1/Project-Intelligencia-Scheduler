import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    year = Column(Integer, nullable=False)  # Academic year (1st year, 2nd year, etc.)
    size = Column(Integer, nullable=False)  # Number of students in the batch
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    department = relationship("Department", back_populates="batches")
    institution = relationship("Institution", back_populates="batches")
    faculty_preferences = relationship("FacultyTeachingPreference", back_populates="batch")
    constraints = relationship("SchedulingConstraint", back_populates="batch")
    sessions = relationship("ScheduledSession", back_populates="batch")
