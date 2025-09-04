import logging
from typing import Dict, Any

import config

class BouncerPolicy:
    """Implements the dynamic, score-based bouncer policy."""

    def __init__(self, constraints: list, attribute_statistics: dict):
        """Initializes the policy with the game's constraints and statistics."""
        self.constraints = {c["attribute"]: c["minCount"] for c in constraints}
        self.frequencies = attribute_statistics["relativeFrequencies"]
        self.attribute_ids = list(self.frequencies.keys())
        logging.info(f"Policy initialized with constraints: {self.constraints}")

    def decide(self, person_attributes: Dict[str, bool], game_state: Dict[str, Any]) -> bool:
        """Makes the accept/reject decision for a given person."""
        admitted_count = game_state["admittedCount"]
        admitted_stats = game_state["admittedAttributes"]

        n_remaining = config.VENUE_CAPACITY - admitted_count
        if n_remaining <= 0:
            return False  # Cannot admit if the club is full

        # 1. Check if all constraints are already met. If so, accept everyone.
        constraints_met = all(
            admitted_stats.get(attr, 0) >= min_count
            for attr, min_count in self.constraints.items()
        )
        if constraints_met:
            logging.info("All constraints met. Accepting to fill the venue.")
            return True

        # 2. Calculate attribute values based on scarcity
        attribute_values = {}
        for attr in self.attribute_ids:
            needed = self.constraints.get(attr, 0) - admitted_stats.get(attr, 0)
            if needed <= 0:
                attribute_values[attr] = 0
                continue

            required_rate = needed / n_remaining
            arrival_rate = self.frequencies.get(attr, 0)

            if arrival_rate > 0:
                attribute_values[attr] = required_rate / arrival_rate
            else: # Attribute is needed but will never arrive
                attribute_values[attr] = float('inf') if required_rate > 0 else 0

        # 3. Score the current person
        person_score = sum(
            attribute_values.get(attr, 0)
            for attr, has_attr in person_attributes.items()
            if has_attr
        )

        # 4. Determine the acceptance threshold (opportunity cost)
        expected_score_of_next_person = sum(
            self.frequencies.get(attr, 0) * attribute_values.get(attr, 0)
            for attr in self.attribute_ids
        )

        # 5. Make the decision
        decision = person_score >= expected_score_of_next_person

        # logging.debug(f"Person Score: {person_score:.2f}, Threshold: {expected_score_of_next_person:.2f}. Decision: {'Accept' if decision else 'Reject'}")

        return decision
