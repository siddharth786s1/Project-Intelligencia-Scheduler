"""
Base algorithm module for the scheduler service.
Provides common functionality for scheduling algorithms.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from uuid import UUID

class BaseSchedulingAlgorithm(ABC):
    """
    Base class for all scheduling algorithms.
    Defines the common interface that all scheduling algorithms must implement.
    """
    
    def __init__(self, data: Dict[str, Any], parameters: Dict[str, Any]):
        """
        Initialize the scheduling algorithm with the necessary data.
        
        Args:
            data: A dictionary containing all the data needed for scheduling
                 (faculty, batches, subjects, classrooms, time_slots, constraints)
            parameters: Algorithm-specific parameters
        """
        self.faculty = data.get("faculty", [])
        self.batches = data.get("batches", [])
        self.subjects = data.get("subjects", [])
        self.classrooms = data.get("classrooms", [])
        self.time_slots = data.get("time_slots", [])
        self.constraints = data.get("constraints", [])
        self.parameters = parameters
        
        # Additional data structures to help with scheduling
        self.faculty_by_id = {faculty["id"]: faculty for faculty in self.faculty}
        self.batch_by_id = {batch["id"]: batch for batch in self.batches}
        self.subject_by_id = {subject["id"]: subject for subject in self.subjects}
        self.classroom_by_id = {classroom["id"]: classroom for classroom in self.classrooms}
        self.time_slot_by_id = {time_slot["id"]: time_slot for time_slot in self.time_slots}
        
        # Processed faculty preferences for easier access
        self.faculty_preferences = self._process_faculty_preferences()
        
    def _process_faculty_preferences(self) -> Dict[UUID, Dict[str, Any]]:
        """
        Process faculty preferences into a more accessible format.
        
        Returns:
            A dictionary mapping faculty IDs to their processed preferences.
        """
        processed_preferences = {}
        
        for faculty in self.faculty:
            faculty_id = faculty["id"]
            preferences = faculty.get("preferences", {})
            
            processed_preferences[faculty_id] = {
                "availability": self._process_availability(preferences.get("availability", [])),
                "subject_expertise": self._process_subject_expertise(preferences.get("subject_expertise", [])),
                "batch_preferences": self._process_batch_preferences(preferences.get("batch_preferences", [])),
                "classroom_preferences": self._process_classroom_preferences(preferences.get("classroom_preferences", []))
            }
            
        return processed_preferences
    
    def _process_availability(self, availability: List[Dict[str, Any]]) -> Dict[str, Dict[str, bool]]:
        """
        Process faculty availability into a more accessible format.
        
        Args:
            availability: List of availability objects
            
        Returns:
            A dictionary mapping day of week to time slot type to availability
        """
        processed = {}
        for avail in availability:
            day = avail.get("day_of_week")
            time_slot = avail.get("time_slot")
            is_available = avail.get("is_available", True)
            
            if day not in processed:
                processed[day] = {}
            
            processed[day][time_slot] = is_available
            
        return processed
    
    def _process_subject_expertise(self, expertise: List[Dict[str, Any]]) -> Dict[UUID, int]:
        """
        Process subject expertise into a more accessible format.
        
        Args:
            expertise: List of subject expertise objects
            
        Returns:
            A dictionary mapping subject IDs to expertise levels (1-5)
        """
        processed = {}
        for exp in expertise:
            subject_id = exp.get("subject_id")
            level = exp.get("expertise_level")
            
            # Convert expertise level to a numeric value (1-5)
            level_value = {
                "NOVICE": 1,
                "INTERMEDIATE": 2,
                "ADVANCED": 4,
                "EXPERT": 5
            }.get(level, 3)  # Default to INTERMEDIATE (3)
            
            processed[subject_id] = level_value
            
        return processed
    
    def _process_batch_preferences(self, preferences: List[Dict[str, Any]]) -> Dict[UUID, int]:
        """
        Process batch preferences into a more accessible format.
        
        Args:
            preferences: List of batch preference objects
            
        Returns:
            A dictionary mapping batch IDs to preference levels (-2 to +2)
        """
        processed = {}
        for pref in preferences:
            batch_id = pref.get("batch_id")
            level = pref.get("preference_level")
            
            # Convert preference level to a numeric value (-2 to +2)
            level_value = {
                "STRONGLY_DISLIKE": -2,
                "DISLIKE": -1,
                "NEUTRAL": 0,
                "PREFER": 1,
                "STRONGLY_PREFER": 2
            }.get(level, 0)  # Default to NEUTRAL (0)
            
            processed[batch_id] = level_value
            
        return processed
    
    def _process_classroom_preferences(self, preferences: List[Dict[str, Any]]) -> Dict[UUID, int]:
        """
        Process classroom preferences into a more accessible format.
        
        Args:
            preferences: List of classroom preference objects
            
        Returns:
            A dictionary mapping classroom IDs to preference levels (-2 to +2)
        """
        processed = {}
        for pref in preferences:
            classroom_id = pref.get("classroom_id")
            level = pref.get("preference_level")
            
            # Convert preference level to a numeric value (-2 to +2)
            level_value = {
                "STRONGLY_DISLIKE": -2,
                "DISLIKE": -1,
                "NEUTRAL": 0,
                "PREFER": 1,
                "STRONGLY_PREFER": 2
            }.get(level, 0)  # Default to NEUTRAL (0)
            
            processed[classroom_id] = level_value
            
        return processed
    
    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """
        Run the scheduling algorithm.
        
        Returns:
            A dictionary containing the scheduling results, including:
            - scheduled_sessions: List of scheduled sessions
            - metrics: Dictionary of metrics about the schedule quality
        """
        pass
    
    def calculate_metrics(self, scheduled_sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate metrics for the scheduled sessions.
        
        Args:
            scheduled_sessions: List of scheduled sessions
            
        Returns:
            A dictionary containing metrics about the schedule quality
        """
        # Base implementation with placeholder metrics
        return {
            "hard_constraint_violations": 0,
            "soft_constraint_violations": 0,
            "faculty_satisfaction_score": 0.0,
            "batch_satisfaction_score": 0.0,
            "room_utilization": 0.0
        }
