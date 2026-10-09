"""Script to load data from Riot API."""
import os
import logging
import requests as req
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

DEFAULT_REGION = "europe"
DEFAULT_GAMENAME = "RidTheKid"
DEFAULT_TAG = "567"


def get_api_key() -> str:
    """Returns Riot API Key from environment."""
    api_key = os.getenv("RIOT_API_KEY")
    if not api_key:
        logging.error("Riot API Key is not defined in environment.")
        raise EnvironmentError("Missing Riot API Key")
    if not isinstance(api_key, str):
        logging.error("Invalid Riot API Key (Must be string format).")
        raise TypeError("Riot API Key must be of string format.")
    if "RGAPI" not in api_key:
        logging.error("Invalid Riot API Key (Requires 'RGAPI' prefix).")
        raise ValueError("Riot API Key must start with 'RGAPI' prefix!")
    if len(api_key) != 42:
        logging.error("Invalid Riot API Key (Must be 42 characters long).")
        raise ValueError("Riot API Key must have 42 characters!")
    return api_key


def load_riot_id(region: str, game_name: str, tag: str) -> str:
    """Returns id associated to a riot account."""
    try:
        api_key = get_api_key()
    except (EnvironmentError, TypeError, ValueError):
        return None
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
    url += f"{game_name}/{tag}?api_key={api_key}"
    try:
        response = req.get(url, timeout=5)
        response.raise_for_status()
    except req.HTTPError as e:
        logging.error(
            f"Failed to get data from Riot API\nError:{e}\nURL: {url}")
        return None
    data = response.json()
    riot_id = data.get("puuid")
    if not riot_id:
        logging.error(f"Response data has no puuid key: {data}")
        return None
    logger.info("Riot ID retrieved successfully.")
    return riot_id


if __name__ == "__main__":
    riot_id = load_riot_id(DEFAULT_REGION, DEFAULT_GAMENAME, DEFAULT_TAG)
    print(riot_id)
