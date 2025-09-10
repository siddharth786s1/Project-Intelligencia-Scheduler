from uuid import UUID
from typing import Optional, List, Dict
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, validator


class WeekDay(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class TimeSlotType(str, Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"
    ANY = "ANY"


class ExpertiseLevel(str, Enum):
    NOVICE = "NOVICE"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class PreferenceLevel(str, Enum):
    STRONGLY_DISLIKE = "STRONGLY_DISLIKE"
    DISLIKE = "DISLIKE"
    NEUTRAL = "NEUTRAL"
    PREFER = "PREFER"
    STRONGLY_PREFER = "STRONGLY_PREFER"


# Faculty Availability Schemas
class FacultyAvailabilityBase(BaseModel):
    day_of_week: WeekDay
    time_slot: TimeSlotType
    is_available: bool = True


class FacultyAvailabilityCreate(FacultyAvailabilityBase):
    faculty_id: UUID


class FacultyAvailabilityUpdate(BaseModel):
    is_available: bool


class FacultyAvailabilityResponse(FacultyAvailabilityBase):
    id: UUID
    faculty_id: UUID
    
    model_config = ConfigDict(from_attributes=True)


# Faculty Subject Expertise Schemas
class FacultySubjectExpertiseBase(BaseModel):
    subject_id: UUID
    expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE


class FacultySubjectExpertiseCreate(FacultySubjectExpertiseBase):
    faculty_id: UUID


class FacultySubjectExpertiseUpdate(BaseModel):
    expertise_level: Optional[ExpertiseLevel] = None


class FacultySubjectExpertiseResponse(FacultySubjectExpertiseBase):
    id: UUID
    faculty_id: UUID
    subject_name: str  # For convenience in responses
    
    model_config = ConfigDict(from_attributes=True)


# Faculty Batch Preference Schemas
class FacultyBatchPreferenceBase(BaseModel):
    batch_id: UUID
    preference_level: PreferenceLevel = PreferenceLevel.NEUTRAL


class FacultyBatchPreferenceCreate(FacultyBatchPreferenceBase):
    faculty_id: UUID


class FacultyBatchPreferenceUpdate(BaseModel):
    preference_level: PreferenceLevel


class FacultyBatchPreferenceResponse(FacultyBatchPreferenceBase):
    id: UUID
    faculty_id: UUID
    batch_name: str  # For convenience in responses
    
    model_config = ConfigDict(from_attributes=True)


# Faculty Classroom Preference Schemas
class FacultyClassroomPreferenceBase(BaseModel):
    classroom_id: UUID
    preference_level: PreferenceLevel = PreferenceLevel.NEUTRAL


class FacultyClassroomPreferenceCreate(FacultyClassroomPreferenceBase):
    faculty_id: UUID


class FacultyClassroomPreferenceUpdate(BaseModel):
    preference_level: PreferenceLevel


class FacultyClassroomPreferenceResponse(FacultyClassroomPreferenceBase):
    id: UUID
    faculty_id: UUID
    classroom_name: str  # For convenience in responses
    
    model_config = ConfigDict(from_attributes=True)


# Combined Faculty Preferences Response
class FacultyPreferencesResponse(BaseModel):
    faculty_id: UUID
    availability: List[FacultyAvailabilityResponse] = []
    subject_expertise: List[FacultySubjectExpertiseResponse] = []
    batch_preferences: List[FacultyBatchPreferenceResponse] = []
    classroom_preferences: List[FacultyClassroomPreferenceResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
