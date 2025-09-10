import uuid
from datetime import datetime, time
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Time, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # e.g., "Morning 1", "Afternoon 2"
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0 = Monday, 6 = Sunday
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Ensure end_time is after start_time
    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_timeslot_valid'),
        CheckConstraint('day_of_week >= 0 AND day_of_week <= 6', name='check_day_of_week_valid'),
    )
    
    # Relationships
    institution = relationship("Institution", back_populates="time_slots")
    sessions = relationship("ScheduledSession", back_populates="time_slot")
    
    def __str__(self):
        return f"{self.name} ({self.start_time}-{self.end_time})"
