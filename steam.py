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


def load_users(steam_ids: list[int]) -> list:
    """Returns data associated to a steam account."""
    api_key = os.getenv("STEAM_API_KEY")
    if not isinstance(api_key, str):
        logging.error("Invalid Steam API Key")
        raise TypeError("Steam API Key must be of string format.")
    if len(api_key) != 32:
        logging.error("Invalid Steam API Key")
        raise ValueError("Steam API Key must have 32 characters!")
    if not isinstance(steam_ids, list):
        if isinstance(steam_ids, int):
            logging.debug(
                f"Steam ID inputted as a single integer, not list: {steam_ids}")
            steam_ids = [steam_ids]
        elif isinstance(steam_ids, str) and steam_ids.isnumeric():
            logging.debug(
                f"Steam ID inputted as a single integer in string format, not list: {steam_ids}")
            steam_ids = [int(steam_ids)]
        else:
            logging.error(f"IDs are in invalid format: {steam_ids}")
            return []
    valid_ids = []
    for steam_id in steam_ids:
        if not str(steam_id).isnumeric():
            logging.info(f"Invalid ID: {steam_id}")
        else:
            valid_ids.append(str(steam_id))
    if not valid_ids:
        logging.error(f"No Valid IDs: {steam_ids}")
        return []
    ids = ",".join(valid_id for valid_id in valid_ids)
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={ids}"
    try:
        response = req.get(url, timeout=5)
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


if __name__ == "__main__":
    ids = [EXAMPLE_STEAM_ID]
    user_data = load_users(ids)
    print(user_data)
