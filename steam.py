"""Script to load data from Steam Account using Steam API"""
import os
import logging
import requests as req
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


EXAMPLE_STEAM_ID = 76561197960435530


def get_api_key() -> str:
    """Returns Steam API Key from environment."""
    api_key = os.getenv("STEAM_API_KEY")
    if not api_key:
        logging.error("Steam API Key is not defined in environment.")
        raise EnvironmentError("Missing Steam API Key")
    if not isinstance(api_key, str):
        logging.error("Invalid Steam API Key")
        raise TypeError("Steam API Key must be of string format.")
    if len(api_key) != 32:
        logging.error("Invalid Steam API Key")
        raise ValueError("Steam API Key must have 32 characters!")
    return api_key


def validate_steam_ids(ids: list[int]) -> list[int]:
    """Validates input steam ids as correctly formatted."""
    if not isinstance(ids, list):
        if isinstance(ids, int):
            logging.debug(
                f"Steam ID inputted as a single integer, not list: {ids}")
            ids = [ids]
        elif isinstance(ids, str) and ids.isnumeric():
            logging.debug(
                f"Steam ID inputted as a single integer in string format, not list: {ids}")
            ids = [int(ids)]
        else:
            logging.error(f"IDs are in invalid format: {ids}")
            return []
    valid_ids = []
    for steam_id in ids:
        if not str(steam_id).isnumeric():
            logging.info(f"Invalid ID: {steam_id}")
        else:
            valid_ids.append(str(steam_id))
    if not valid_ids:
        logging.error(f"No Valid IDs: {ids}")
        return []
    return valid_ids


def load_users(steam_ids: list[int]) -> list:
    """Returns data associated to a steam account."""
    try:
        api_key = get_api_key()
    except (EnvironmentError, TypeError, ValueError):
        return []
    valid_ids = validate_steam_ids(steam_ids)
    if not valid_ids:
        return []
    ids = ",".join(valid_id for valid_id in valid_ids)
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    url += f"?key={api_key}&steamids={ids}"
    try:
        response = req.get(url, timeout=5)
        response.raise_for_status()
    except req.HTTPError as e:
        logging.error(
            f"Failed to get data from Steam API\nError:{e}\nURL: {url}")
        return []
    data = response.json()
    user_data = data.get("response", {}).get("players", [])
    if not user_data:
        logging.error(f"Response data is in invalid format: {data}")
        return []
    logger.info("User data retrieved successfully.")
    return user_data


def load_games(steam_id: int, include: bool = False) -> tuple(int, list):
    """Returns all owned games by the player and played free games as well."""
    try:
        api_key = get_api_key()
    except (TypeError, ValueError):
        return None, []
    steam_id = validate_steam_ids(steam_id)
    if not steam_id:
        return None, []
    steam_id = steam_id[0]
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    url += f"?key={api_key}&steamid={steam_id}&format=json&include_appinfo=true"
    if include:
        url += "&include_played_free_games=true"
    try:
        response = req.get(url, timeout=5)
        response.raise_for_status()
    except req.HTTPError as e:
        logging.error(
            f"Failed to get data from Steam API\nError:{e}\nURL: {url}")
        return None, []
    data = response.json()
    games_data = data.get("response", {})
    game_count = games_data.get("game_count", None)
    games = games_data.get("games", [])
    return game_count, games


if __name__ == "__main__":
    # ids = [EXAMPLE_STEAM_ID]
    # user_data = load_users(ids)
    # print(user_data)
    steam_id = os.getenv("STEAM_ID")
    print(steam_id)
    print(load_games(steam_id))
