"""Test Suite for Steam functions."""
from unittest.mock import patch, MagicMock
import logging
import pytest
from requests import HTTPError
from steam import (EXAMPLE_STEAM_ID, get_api_key, validate_steam_ids,
                   load_users, load_games)


class TestGetAPIKey:
    @patch("steam.os.getenv")
    def test_invalid_api_key_1(self, invalid_key, caplog):
        caplog.set_level(logging.ERROR)
        invalid_key.return_value = None
        with pytest.raises(EnvironmentError):
            get_api_key()
        message = "Steam API Key is not defined in environment."
        assert message in caplog.text

    @patch("steam.os.getenv")
    def test_invalid_api_key_2(self, invalid_key, caplog):
        caplog.set_level(logging.ERROR)
        invalid_key.return_value = 123
        with pytest.raises(TypeError):
            get_api_key()
        message = "Invalid Steam API Key (Must be string format)."
        assert message in caplog.text

    @patch("steam.os.getenv")
    def test_invalid_api_key_3(self, invalid_key, caplog):
        caplog.set_level(logging.ERROR)
        invalid_key.return_value = "XA23BDC312MSD45"
        with pytest.raises(ValueError):
            get_api_key()
        message = "Invalid Steam API Key (Must be 32 characters long)."
        assert message in caplog.text

    @patch("steam.os.getenv")
    def test_valid_api_key(self, valid_key):
        valid_key.return_value = "A" * 32
        assert get_api_key() == "A" * 32


class TestValidateSteamIDs:
    @patch("steam.os.getenv")
    def test_invalid_ids_format(self, valid_key, caplog):
        caplog.set_level(logging.ERROR)
        valid_key.return_value = "A" * 32
        invalid_ids = {"id": 1234343512}
        message = f"IDs are in invalid format: {invalid_ids}"
        result = validate_steam_ids(invalid_ids)
        assert result == []
        assert message in caplog.text

    @patch("steam.os.getenv")
    def test_invalid_ids(self, valid_key, caplog):
        caplog.set_level(logging.ERROR)
        valid_key.return_value = "A" * 32
        invalid_ids = ["A213123"]
        message = f"No Valid IDs: {invalid_ids}"
        result = validate_steam_ids(invalid_ids)
        assert result == []
        assert message in caplog.text

    @patch("steam.os.getenv")
    def test_valid_ids(self, valid_key):
        valid_key.return_value = "A" * 32
        valid_ids = ["123123123", 111000]
        result = validate_steam_ids(valid_ids)
        assert result == ["123123123", "111000"]


class TestLoadUsers:
    @patch("requests.get")
    @patch("steam.os.getenv")
    def test_failed_request(self, valid_key, invalid_response, caplog):
        caplog.set_level(logging.ERROR)
        valid_key.return_value = "A" * 32
        invalid_response.side_effect = HTTPError("404 Client Error")
        ids = [123123123]
        message = f"Failed to get data from Steam API\nError:"
        result = load_users(ids)
        assert result == []
        assert message in caplog.text

    @patch("requests.get")
    @patch("steam.os.getenv")
    def test_invalid_response_format(self, valid_key, invalid_response, caplog):
        caplog.set_level(logging.ERROR)
        valid_key.return_value = "A" * 32
        invalid_data = {"response":
                        {"members":
                         [{"steam_id": "123123123"}]
                         }
                        }
        invalid_response.return_value.json.return_value = invalid_data
        ids = [123123123]
        message = f"Response data is in invalid format:"
        result = load_users(ids)
        assert result == []
        assert message in caplog.text

    @patch("requests.get")
    @patch("steam.os.getenv")
    def test_valid_ids(self, valid_key, valid_response):
        valid_key.return_value = "A" * 32
        valid_response.return_value.json.return_value = {"response":
                                                         {"players":
                                                          [{"steam_id": "123123123"},
                                                           {"steam_id": "111000"}]
                                                          }
                                                         }
        ids = [123123123, 111000]
        result = load_users(ids)
        assert result == [{"steam_id": "123123123"}, {"steam_id": "111000"}]

    @patch("requests.get")
    @patch("steam.os.getenv")
    def test_valid_single_string_id(self, valid_key, valid_response, caplog):
        caplog.set_level(logging.DEBUG)
        valid_key.return_value = "A" * 32
        valid_response.return_value.json.return_value = {"response":
                                                         {"players":
                                                          [{"steam_id": "123123123"}]
                                                          }
                                                         }
        ids = 123123123
        message = f"Steam ID inputted as a single integer, not list: {ids}"
        result = load_users(ids)
        assert result == [{"steam_id": "123123123"}]
        assert message in caplog.text


class TestLoadGames:
    @patch("requests.get")
    @patch("steam.os.getenv")
    def test_failed_request(self, valid_key, invalid_response, caplog):
        caplog.set_level(logging.ERROR)
        valid_key.return_value = "A" * 32
        invalid_response.side_effect = HTTPError("404 Client Error")
        ids = [123123123]
        message = f"Failed to get data from Steam API\nError:"
        result = load_games(ids)
        assert result == (None, [])
        assert message in caplog.text

    @patch("requests.get")
    @patch("steam.os.getenv")
    def test_valid_response(self, valid_key, valid_response):
        valid_key.return_value = "A" * 32
        valid_response.return_value.json.return_value = {"response":
                                                         {"game_count": 10,
                                                          "games": [{"name": "GTA"}]
                                                          }
                                                         }
        ids = [123123123]
        game_count, games = load_games(ids)
        assert game_count == 10
        assert games == [{"name": "GTA"}]
