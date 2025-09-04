import argparse
import logging

import config
from api_client import APIClient
from bouncer_policy import BouncerPolicy

def run_game(scenario: int):
    """Initializes and runs a single game scenario."""
    logging.info(f"Starting game for scenario {scenario}...")
    client = APIClient(player_id=config.PLAYER_ID)

    # Start new game and initialize policy
    initial_response = client.new_game(scenario)
    game_id = initial_response["gameId"]
    logging.info(f"New game started with ID: {game_id}")

    policy = BouncerPolicy(
        constraints=initial_response["constraints"],
        attribute_statistics=initial_response["attributeStatistics"],
    )

    # Get the first person
    response = client.decide_and_next(game_id, person_index=0)

    # Game state tracker.
    # NOTE: The API does not provide a running total of admitted attributes,
    # only the total count. We must track the attribute breakdown locally to
    # inform our policy. This is a potential point of divergence if an API
    # call fails permanently after being retried, but is a necessary
    # implementation detail given the API's design.
    admitted_attributes_tracker = {
        attr: 0 for attr in policy.attribute_ids
    }

    while response.get("status") == "running":
        person = response["nextPerson"]
        person_index = person["personIndex"]
        person_attributes = person["attributes"]

        game_state = {
            "admittedCount": response["admittedCount"],
            "admittedAttributes": admitted_attributes_tracker,
        }

        # Decide
        accept = policy.decide(person_attributes, game_state)

        # Act and update state
        if accept:
            for attr, has_attr in person_attributes.items():
                if has_attr:
                    admitted_attributes_tracker[attr] += 1

        logging.info(
            f"Person {person_index}: {'Accepted' if accept else 'Rejected'}. "
            f"Admitted: {response['admittedCount']}/{config.VENUE_CAPACITY}. "
            f"Rejected: {response['rejectedCount']}."
        )

        response = client.decide_and_next(game_id, person_index, accept)

    # Game finished
    final_status = response.get("status")
    if final_status == "completed":
        logging.info(
            "Game completed successfully! "
            f"Final rejected count: {response['rejectedCount']}"
        )
    else:
        logging.error(
            f"Game failed! Reason: {response.get('reason', 'Unknown')}"
        )

def main():
    """
    Main entry point for the application.
    Parses command-line arguments and starts the game.
    """
    config.setup_logging()

    parser = argparse.ArgumentParser(description="Berghain Bouncer Challenge")
    parser.add_argument(
        "scenario",
        type=int,
        choices=[1, 2, 3],
        help="The scenario number to run (1, 2, or 3)."
    )
    args = parser.parse_args()

    try:
        run_game(args.scenario)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
