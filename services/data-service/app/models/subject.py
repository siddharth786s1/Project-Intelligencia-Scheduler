import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    credits = Column(Integer, nullable=False)
    lecture_hours_per_week = Column(Integer, nullable=False)
    lab_hours_per_week = Column(Integer, nullable=False, default=0)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    department = relationship("Department", back_populates="subjects")
    institution = relationship("Institution", back_populates="subjects")
    # Other relationships would be defined here (faculty assignments, batch associations, etc.)
