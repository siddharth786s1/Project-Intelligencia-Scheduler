# Define __init__.py files for each directory to enable proper Python importing

from .institution_repository import InstitutionRepository
from .department_repository import DepartmentRepository
from .classroom_repository import ClassroomRepository
from .room_type_repository import RoomTypeRepository
from .subject_repository import SubjectRepository
from .batch_repository import BatchRepository
from .faculty_repository import FacultyRepository
from .faculty_preferences_repository import (
    FacultyAvailabilityRepository,
    FacultySubjectExpertiseRepository,
    FacultyTeachingPreferenceRepository
)
