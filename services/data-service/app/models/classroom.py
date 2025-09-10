import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Classroom(Base):
    __tablename__ = "classrooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    room_type_id = Column(UUID(as_uuid=True), ForeignKey("room_types.id"), nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    institution = relationship("Institution", back_populates="classrooms")
    room_type = relationship("RoomType", back_populates="classrooms")
    faculty_preferences = relationship("FacultyTeachingPreference", back_populates="classroom")
    constraints = relationship("SchedulingConstraint", back_populates="classroom")
    sessions = relationship("ScheduledSession", back_populates="classroom")
