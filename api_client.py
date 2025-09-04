import logging
import requests
from requests.adapters import HTTPAdapter, Retry

import config

class APIClient:
    """A resilient API client for the Berghain Challenge."""

    def __init__(self, player_id: str):
        self.player_id = player_id
        self.base_url = config.BASE_URL
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Creates a requests session with connection hardening and retries."""
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=frozenset(["POST", "GET"]),
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def new_game(self, scenario: int) -> dict:
        """Starts a new game for the given scenario."""
        url = f"{self.base_url}/new-game"
        params = {"scenario": scenario, "playerId": self.player_id}
        try:
            response = self._session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API call to new_game failed: {e}")
            raise

    def decide_and_next(
        self, game_id: str, person_index: int, accept: bool = None
    ) -> dict:
        """
        Gets the next person and makes a decision.
        The 'accept' parameter is omitted for the first call (person_index == 0).
        """
        url = f"{self.base_url}/decide-and-next"
        params = {"gameId": game_id, "personIndex": person_index}
        if accept is not None:
            params["accept"] = str(accept).lower()

        try:
            response = self._session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API call to decide_and_next failed: {e}")
            raise
