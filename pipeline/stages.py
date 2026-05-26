from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseStage(ABC):
    """
    Abstract Base Class for a compiler stage in the AI Compiler pipeline.
    Each stage takes a compilation context dictionary, performs its logic, 
    updates the context, and returns it.
    """
    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the stage logic.
        
        Args:
            context: Current compilation context containing parameters, 
                     intermediate designs, configurations, and logs.
                     
        Returns:
            Updated compilation context.
        """
        pass
