import requests
from collections import Counter
import pytest
from unittest.mock import patch, Mock


class APIError(Exception):
    pass

class CatFactProcessor:
    def __init__(self):
        self.last_fact = ""

    def get_fact(self):
        try:
            response = requests.get("https://catfact.ninja/fact")
            response.raise_for_status()
            data = response.json()
            self.last_fact = data["fact"]
            return self.last_fact
        except requests.exceptions.RequestException as e:
            raise APIError(f"Ошибка при запросе к API: {e}") from e

    def get_fact_analysis(self):
        if not self.last_fact:
            return {"length": 0, "letter_frequencies": {}}
        fact_length = len(self.last_fact)
        letter_frequencies = dict(Counter(self.last_fact.lower()))
        return {
            "length": fact_length,
            "letter_frequencies": letter_frequencies,
        }

#тесты

@patch("cat.requests.get")
def test_get_fact_success(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"fact": "Cats sleep 70% of their lives."}
    mock_get.return_value = mock_response

    processor = CatFactProcessor()
    fact = processor.get_fact()

    assert fact == "Cats sleep 70% of their lives."
    assert processor.last_fact == fact

@patch("cat.requests.get")
def test_get_fact_api_error(mock_get):
    import requests
    mock_get.side_effect = requests.exceptions.RequestException("Connection failed")

    processor = CatFactProcessor()
    with pytest.raises(APIError) as exc_info:
        processor.get_fact()
    assert "Ошибка при запросе к API" in str(exc_info.value)

def test_get_fact_analysis_valid():
    processor = CatFactProcessor()
    processor.last_fact = "Cat"

    result = processor.get_fact_analysis()

    assert result["length"] == 3
    assert result["letter_frequencies"] == {'c': 1, 'a': 1, 't': 1}

def test_get_fact_analysis_empty():
    processor = CatFactProcessor()
    processor.last_fact = ""

    result = processor.get_fact_analysis()

    assert result["length"] == 0
    assert result["letter_frequencies"] == {}
