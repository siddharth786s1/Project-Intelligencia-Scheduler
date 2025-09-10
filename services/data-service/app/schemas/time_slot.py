from uuid import UUID
from datetime import time
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, validator
from enum import Enum


class DayOfWeek(int, Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class TimeSlotBase(BaseModel):
    name: str
    start_time: time
    end_time: time
    day_of_week: DayOfWeek
    is_active: bool = True
    
    @validator('end_time')
    def check_end_time_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class TimeSlotCreate(TimeSlotBase):
    pass


class TimeSlotUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    day_of_week: Optional[DayOfWeek] = None
    is_active: Optional[bool] = None
    
    @validator('end_time')
    def check_end_time_after_start_time(cls, v, values):
        if v is not None and 'start_time' in values and values['start_time'] is not None and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class TimeSlotResponse(TimeSlotBase):
    id: UUID
    institution_id: UUID
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def display_day(self) -> str:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[self.day_of_week]
    
    @property
    def display_time(self) -> str:
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
