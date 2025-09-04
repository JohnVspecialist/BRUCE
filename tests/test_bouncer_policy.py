import pytest
from bouncer_policy import BouncerPolicy

@pytest.fixture
def base_stats():
    """Provides a base set of attribute statistics."""
    return {
        "relativeFrequencies": {
            "local": 0.4,
            "regular": 0.2,
            "all_black": 0.6
        },
        "correlations": {}
    }

def test_initialization(base_stats):
    """Tests that the policy initializes correctly."""
    constraints = [{"attribute": "local", "minCount": 400}]
    policy = BouncerPolicy(constraints, base_stats)
    assert policy.constraints["local"] == 400
    assert policy.frequencies["local"] == 0.4

def test_accept_when_constraints_met(base_stats):
    """Tests that the policy always accepts when all constraints are met."""
    constraints = [{"attribute": "local", "minCount": 400}]
    policy = BouncerPolicy(constraints, base_stats)

    game_state = {
        "admittedCount": 800,
        "admittedAttributes": {"local": 401, "regular": 100, "all_black": 500}
    }
    person = {"attributes": {"local": False, "regular": True, "all_black": True}}

    assert policy.decide(person["attributes"], game_state) is True

def test_reject_when_full(base_stats):
    """Tests that the policy rejects when the venue is full."""
    constraints = [{"attribute": "local", "minCount": 400}]
    policy = BouncerPolicy(constraints, base_stats)

    game_state = {
        "admittedCount": 1000,
        "admittedAttributes": {"local": 399, "regular": 100, "all_black": 500}
    }
    person = {"attributes": {"local": True, "regular": True, "all_black": True}}

    assert policy.decide(person["attributes"], game_state) is False

def test_prioritize_scarce_attribute(base_stats):
    """
    Tests that the policy correctly prioritizes a person with a needed,
    scarce attribute over a person without it.
    """
    # Scenario: We need 200 regulars, but only 20% of people are regulars.
    # This attribute is "scarce" relative to our need.
    constraints = [{"attribute": "regular", "minCount": 200}]
    policy = BouncerPolicy(constraints, base_stats)

    game_state = {
        "admittedCount": 500, # 500 spots left
        "admittedAttributes": {"local": 200, "regular": 0, "all_black": 300}
    }
    # We need 200 regulars in 500 spots (required rate = 0.4).
    # Arrival rate is 0.2. Value of "regular" should be high (0.4/0.2 = 2.0).

    person_with_scarce_attr = {"attributes": {"local": False, "regular": True, "all_black": False}}
    person_without_scarce_attr = {"attributes": {"local": True, "regular": False, "all_black": True}}

    # The decision logic compares person_score to a threshold.
    # We expect the person with the scarce attribute to be accepted.
    assert policy.decide(person_with_scarce_attr["attributes"], game_state) is True
    # We expect the person without the scarce attribute to be rejected in this state.
    # Note: This might be flaky depending on other attribute values, but in this
    # simple case, "regular" is the only needed attribute.
    assert policy.decide(person_without_scarce_attr["attributes"], game_state) is False
