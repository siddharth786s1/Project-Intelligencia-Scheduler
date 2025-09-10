import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum, JSON, CheckConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class ConstraintType(str, enum.Enum):
    HARD = "hard"  # Must be satisfied
    SOFT = "soft"  # Should be satisfied, but can be violated with penalty


class ConstraintScope(str, enum.Enum):
    FACULTY = "faculty"  # Constraint applies to a specific faculty
    BATCH = "batch"      # Constraint applies to a specific batch
    CLASSROOM = "classroom"  # Constraint applies to a specific classroom
    SUBJECT = "subject"  # Constraint applies to a specific subject
    GLOBAL = "global"    # Constraint applies globally


class SchedulingConstraint(Base):
    __tablename__ = "scheduling_constraints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    constraint_type = Column(Enum(ConstraintType), nullable=False, default=ConstraintType.SOFT)
    scope = Column(Enum(ConstraintScope), nullable=False)
    
    # Target entity IDs - only one should be non-null based on scope
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"), nullable=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=True)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"), nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    
    # JSON configuration for the constraint
    # Structure depends on the constraint type and implementation
    configuration = Column(JSON, nullable=False)
    
    # Weight for soft constraints (higher value means more important)
    weight = Column(Integer, nullable=False, default=1)
    
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    faculty = relationship("Faculty", back_populates="constraints")
    batch = relationship("Batch", back_populates="constraints")
    classroom = relationship("Classroom", back_populates="constraints")
    subject = relationship("Subject", back_populates="constraints")
    institution = relationship("Institution", back_populates="constraints")
    
    # Ensure scope and target entity ID are consistent
    __table_args__ = (
        CheckConstraint(
            """
            (scope = 'faculty' AND faculty_id IS NOT NULL AND batch_id IS NULL AND classroom_id IS NULL AND subject_id IS NULL) OR
            (scope = 'batch' AND faculty_id IS NULL AND batch_id IS NOT NULL AND classroom_id IS NULL AND subject_id IS NULL) OR
            (scope = 'classroom' AND faculty_id IS NULL AND batch_id IS NULL AND classroom_id IS NOT NULL AND subject_id IS NULL) OR
            (scope = 'subject' AND faculty_id IS NULL AND batch_id IS NULL AND classroom_id IS NULL AND subject_id IS NOT NULL) OR
            (scope = 'global' AND faculty_id IS NULL AND batch_id IS NULL AND classroom_id IS NULL AND subject_id IS NULL)
            """,
            name='check_scope_consistency'
        ),
        CheckConstraint(
            'weight >= 1 AND weight <= 10',
            name='check_weight_range'
        ),
    )
