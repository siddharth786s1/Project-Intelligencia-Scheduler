# Define __init__.py files for each directory to enable proper Python importing

from .institution import (
    InstitutionCreate, InstitutionUpdate, InstitutionResponse
)
from .department import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse
)
from .classroom import (
    ClassroomCreate, ClassroomUpdate, ClassroomResponse
)
from .room_type import (
    RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse
)
from .subject import (
    SubjectCreate, SubjectUpdate, SubjectResponse
)
from .batch import (
    BatchCreate, BatchUpdate, BatchResponse
)
from .faculty import (
    FacultyBase, FacultyCreate, FacultyUpdate, FacultyResponse, FacultyDetailResponse
)
from .faculty_preferences import (
    WeekDay, TimeSlotType, ExpertiseLevel, PreferenceLevel,
    FacultyAvailabilityCreate, FacultyAvailabilityUpdate, FacultyAvailabilityResponse,
    FacultySubjectExpertiseCreate, FacultySubjectExpertiseUpdate, FacultySubjectExpertiseResponse,
    FacultyBatchPreferenceCreate, FacultyBatchPreferenceUpdate, FacultyBatchPreferenceResponse,
    FacultyClassroomPreferenceCreate, FacultyClassroomPreferenceUpdate, FacultyClassroomPreferenceResponse,
    FacultyPreferencesResponse
)
from .response import ResponseModel, PaginatedResponseModel
from .common import PaginationParams
