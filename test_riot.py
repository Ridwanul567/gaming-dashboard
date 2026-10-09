"""Test Suite for Riot functions."""
from unittest.mock import patch, MagicMock
import logging
import pytest
from requests import HTTPError
from riot import (DEFAULT_REGION, DEFAULT_GAMENAME, DEFAULT_TAG,
                  get_api_key, load_riot_id)


class TestGetAPIKey:
    @patch("riot.os.getenv")
    def test_invalid_api_key_1(self, invalid_key, caplog):
        caplog.set_level(logging.ERROR)
        invalid_key.return_value = None
        with pytest.raises(EnvironmentError):
            get_api_key()
        message = "Riot API Key is not defined in environment."
        assert message in caplog.text

    @patch("riot.os.getenv")
    def test_invalid_api_key_2(self, invalid_key, caplog):
        caplog.set_level(logging.ERROR)
        invalid_key.return_value = 123
        with pytest.raises(TypeError):
            get_api_key()
        message = "Invalid Riot API Key (Must be string format)."
        assert message in caplog.text

    @patch("riot.os.getenv")
    def test_invalid_api_key_3(self, invalid_key, caplog):
        caplog.set_level(logging.ERROR)
        invalid_key.return_value = "XA23BDC312MSD45"
        with pytest.raises(ValueError):
            get_api_key()
        message = "Invalid Riot API Key (Requires 'RGAPI' prefix)."
        assert message in caplog.text

    @patch("riot.os.getenv")
    def test_invalid_api_key_4(self, invalid_key, caplog):
        caplog.set_level(logging.ERROR)
        invalid_key.return_value = "RGAPI-123123"
        with pytest.raises(ValueError):
            get_api_key()
        message = "Invalid Riot API Key (Must be 42 characters long)."
        assert message in caplog.text

    @patch("riot.os.getenv")
    def test_valid_api_key(self, valid_key):
        valid_key.return_value = "RGAPI" + "-" + "A" * 36
        assert get_api_key() == "RGAPI" + "-" + "A" * 36


class TestLoadRiotID:
    @patch("requests.get")
    @patch("riot.os.getenv")
    def test_failed_request(self, valid_key, invalid_response, caplog):
        caplog.set_level(logging.ERROR)
        valid_key.return_value = "RGAPI" + "-" + "A" * 36
        invalid_response.side_effect = HTTPError("404 Client Error")
        message = f"Failed to get data from Riot API\nError:"
        result = load_riot_id(DEFAULT_REGION, DEFAULT_GAMENAME, DEFAULT_TAG)
        assert result == None
        assert message in caplog.text

    @patch("requests.get")
    @patch("steam.os.getenv")
    def test_response_missing_puiid_key(self, valid_key, invalid_response, caplog):
        caplog.set_level(logging.ERROR)
        valid_key.return_value = "RGAPI" + "-" + "A" * 36
        invalid_response.return_value.json.return_value = {"id": 1}
        message = f"Response data has no puuid key:"
        result = load_riot_id(DEFAULT_REGION, DEFAULT_GAMENAME, DEFAULT_TAG)
        assert result == None
        assert message in caplog.text
