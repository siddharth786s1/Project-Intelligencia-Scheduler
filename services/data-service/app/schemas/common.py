from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Generic, TypeVar

T = TypeVar('T')

class EntityNotFound(Exception):
    """Exception raised when an entity is not found."""
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id {entity_id} not found")
