import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Institution(Base):
    __tablename__ = "institutions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    contact_email = Column(String, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    departments = relationship("Department", back_populates="institution")
    classrooms = relationship("Classroom", back_populates="institution")
    room_types = relationship("RoomType", back_populates="institution")
    subjects = relationship("Subject", back_populates="institution")
    batches = relationship("Batch", back_populates="institution")
    faculty = relationship("Faculty", back_populates="institution")
    faculty_availabilities = relationship("FacultyAvailability", back_populates="institution")
    faculty_expertise = relationship("FacultySubjectExpertise", back_populates="institution")
    faculty_preferences = relationship("FacultyTeachingPreference", back_populates="institution")
    time_slots = relationship("TimeSlot", back_populates="institution")
    constraints = relationship("SchedulingConstraint", back_populates="institution")
    sessions = relationship("ScheduledSession", back_populates="institution")
