import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Faculty(Base):
    __tablename__ = "faculty"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to IAM service user
    name = Column(String, nullable=False)
    employee_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    designation = Column(String, nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    joining_date = Column(DateTime, nullable=True)
    weekly_load_hours = Column(Integer, default=40, nullable=False)  # Default weekly teaching load
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    department = relationship("Department", back_populates="faculty")
    institution = relationship("Institution", back_populates="faculty")
    subject_expertise = relationship("FacultySubjectExpertise", back_populates="faculty")
    availability = relationship("FacultyAvailability", back_populates="faculty")
    teaching_preferences = relationship("FacultyTeachingPreference", back_populates="faculty")
    constraints = relationship("SchedulingConstraint", back_populates="faculty")
    sessions = relationship("ScheduledSession", back_populates="faculty")
