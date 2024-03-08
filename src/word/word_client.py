from typing import Any

import requests
from config.settings import app_settings


def get_word_and_translate() -> tuple[str, Any]:
    url = "https://random-words5.p.rapidapi.com/getRandom"

    headers = {
        "X-RapidAPI-Key": app_settings.api_key,
        "X-RapidAPI-Host": "random-words5.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, timeout=10)

    word = response.text

    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/get"

    querystring = {
        "langpair": "en|ru",
        "q": f"{word}",
        "mt": "1",
        "onlyprivate": "0",
        "de": "a@b.c",
    }

    headers = {
        "X-RapidAPI-Key": app_settings.api_key,
        "X-RapidAPI-Host": "translated-mymemory---"
        "translation-memory.p.rapidapi.com",
    }

    response = requests.get(
        url, headers=headers, params=querystring, timeout=10
    )
    return word, response.json()["responseData"]["translatedText"]


def assert_word(w1: str, w2: str) -> bool:
    w1 = w1.lower()
    w2 = w2.lower()
    len_w1 = len(w1)
    len_w2 = len(w2)
    min_len = min(len_w1, len_w2)
    num_mismatch = sum(c1 != c2 for c1, c2 in zip(w1, w2))
    match_percentage = (min_len - num_mismatch) / min_len * 100
    return match_percentage >= 50
