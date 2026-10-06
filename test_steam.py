"""Test Suite for steam functions."""
from unittest.mock import patch, MagicMock
import logging
import pytest
from requests import HTTPError
from steam import load_users, EXAMPLE_STEAM_ID


class TestLoadUsers:
    @patch("steam.os.getenv")
    def test_load_users_invalid_api_key_1(self, invalid_key):
        invalid_key.return_value = 123
        with pytest.raises(TypeError):
            load_users([EXAMPLE_STEAM_ID])

    @patch("steam.os.getenv")
    def test_load_users_invalid_api_key_2(self, invalid_key):
        invalid_key.return_value = "XA23BDC312MSD45"
        with pytest.raises(ValueError):
            load_users([EXAMPLE_STEAM_ID])

    @patch("steam.os.getenv")
    def test_load_users_invalid_ids_format(self, valid_key, caplog):
        caplog.set_level(logging.ERROR)
        valid_key.return_value = "A" * 32
        invalid_ids = {"id": 1234343512}
        message = f"IDs are in invalid format: {invalid_ids}"
        result = load_users(invalid_ids)
        assert result == []
        assert message in caplog.text

    @patch("steam.os.getenv")
    def test_load_users_invalid_ids(self, valid_key, caplog):
        caplog.set_level(logging.ERROR)
        valid_key.return_value = "A" * 32
        invalid_ids = ["A213123"]
        message = f"No Valid IDs: {invalid_ids}"
        result = load_users(invalid_ids)
        assert result == []
        assert message in caplog.text

    @patch("requests.get")
    @patch("steam.os.getenv")
    def test_load_users_failed_request(self, valid_key, invalid_response, caplog):
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
    def test_load_users_invalid_response_format(self, valid_key, invalid_response, caplog):
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
    def test_load_users_single_string_id(self, valid_key, valid_response, caplog):
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
