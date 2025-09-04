import argparse
import logging

import config
from api_client import APIClient
from bouncer_policy import BouncerPolicy
from game_state import GameState

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

    # Initialize game state
    game_state = GameState()
    game_state.initialize_attributes(policy.attribute_ids)

    # Get the first person
    response = client.decide_and_next(game_id, person_index=0)

    while response.get("status") == "running":
        # Update state with server's view
        game_state.admitted_count = response["admittedCount"]
        game_state.rejected_count = response["rejectedCount"]

        person = response["nextPerson"]
        person_index = person["personIndex"]
        person_attributes = person["attributes"]

        # Decide
        accept = policy.decide(person_attributes, game_state.to_dict())

        # Act and update local state
        if accept:
            game_state.record_acceptance(person_attributes)
        else:
            game_state.record_rejection()

        logging.info(
            f"Person {person_index}: {'Accepted' if accept else 'Rejected'}. "
            f"Admitted: {game_state.admitted_count}/{config.VENUE_CAPACITY}. "
            f"Rejected: {game_state.rejected_count}."
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
