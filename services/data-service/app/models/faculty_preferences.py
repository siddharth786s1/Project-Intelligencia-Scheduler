import uuid
from datetime import datetime, time
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum, Time, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class DayOfWeek(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class FacultyAvailability(Base):
    __tablename__ = "faculty_availability"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"), nullable=False)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Ensure end_time is after start_time
    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_timespan_valid'),
    )
    
    # Relationships
    faculty = relationship("Faculty", back_populates="availability")
    institution = relationship("Institution", back_populates="faculty_availabilities")


class PreferenceType(str, enum.Enum):
    PREFERRED = "preferred"
    NEUTRAL = "neutral"
    AVOID = "avoid"


class FacultySubjectExpertise(Base):
    __tablename__ = "faculty_subject_expertise"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    expertise_level = Column(Integer, nullable=False)  # 1-5 rating
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    faculty = relationship("Faculty", back_populates="subject_expertise")
    subject = relationship("Subject", back_populates="faculty_expertise")
    institution = relationship("Institution", back_populates="faculty_expertise")
    
    # Ensure expertise level is between 1 and 5
    __table_args__ = (
        CheckConstraint('expertise_level >= 1 AND expertise_level <= 5', name='check_expertise_level'),
    )


class FacultyTeachingPreference(Base):
    __tablename__ = "faculty_teaching_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"), nullable=True)
    time_slot_preference = Column(Enum(PreferenceType), nullable=False, default=PreferenceType.NEUTRAL)
    preference_type = Column(Enum(PreferenceType), nullable=False)
    preference_weight = Column(Integer, nullable=False, default=3)  # 1-5 weight
    comment = Column(String, nullable=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    faculty = relationship("Faculty", back_populates="teaching_preferences")
    batch = relationship("Batch", back_populates="faculty_preferences")
    subject = relationship("Subject", back_populates="faculty_preferences")
    classroom = relationship("Classroom", back_populates="faculty_preferences")
    institution = relationship("Institution", back_populates="faculty_preferences")
    
    # At least one of batch_id, subject_id, classroom_id must be non-null
    __table_args__ = (
        CheckConstraint(
            'batch_id IS NOT NULL OR subject_id IS NOT NULL OR classroom_id IS NOT NULL',
            name='check_preference_target'
        ),
        CheckConstraint(
            'preference_weight >= 1 AND preference_weight <= 5',
            name='check_preference_weight'
        ),
    )
