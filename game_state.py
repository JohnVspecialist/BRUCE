from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class GameState:
    """Encapsulates the running state of the Berghain game."""
    admitted_count: int = 0
    rejected_count: int = 0

    # Using a field factory to initialize the mutable dictionary
    admitted_attributes: Dict[str, int] = field(default_factory=dict)

    def initialize_attributes(self, attribute_ids: List[str]):
        """Initializes the attribute tracker with all possible attributes."""
        self.admitted_attributes = {attr: 0 for attr in attribute_ids}

    def record_acceptance(self, person_attributes: Dict[str, bool]):
        """Updates the state after a person is accepted."""
        self.admitted_count += 1
        for attr, has_attr in person_attributes.items():
            if has_attr:
                if attr in self.admitted_attributes:
                    self.admitted_attributes[attr] += 1

    def record_rejection(self):
        """Updates the state after a person is rejected."""
        self.rejected_count += 1

    def to_dict(self) -> Dict:
        """Provides a dictionary representation for the policy."""
        return {
            "admittedCount": self.admitted_count,
            "admittedAttributes": self.admitted_attributes
        }
