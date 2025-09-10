"""
Factory module for creating scheduling algorithm instances.
"""
from typing import Dict, Any, Optional, Type

from app.algorithms.base import BaseSchedulingAlgorithm
from app.algorithms.csp import CSPSchedulingAlgorithm
from app.algorithms.genetic import GeneticSchedulingAlgorithm


class AlgorithmFactory:
    """
    Factory for creating scheduling algorithm instances.
    """
    
    _algorithms = {
        "csp": CSPSchedulingAlgorithm,
        "genetic": GeneticSchedulingAlgorithm,
    }
    
    @classmethod
    def create(cls, algorithm_type: str, data: Dict[str, Any], parameters: Dict[str, Any]) -> Optional[BaseSchedulingAlgorithm]:
        """
        Create an instance of the specified algorithm.
        
        Args:
            algorithm_type: Type of algorithm to create ("csp" or "genetic")
            data: Data for the algorithm
            parameters: Algorithm-specific parameters
            
        Returns:
            An instance of the specified algorithm, or None if the type is invalid
        """
        algorithm_class = cls._algorithms.get(algorithm_type.lower())
        
        if algorithm_class:
            return algorithm_class(data, parameters)
        
        return None
    
    @classmethod
    def get_algorithm_types(cls) -> Dict[str, Type[BaseSchedulingAlgorithm]]:
        """
        Get a dictionary of available algorithm types.
        
        Returns:
            A dictionary mapping algorithm type names to their classes
        """
        return cls._algorithms.copy()
