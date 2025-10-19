# lib/rest.py

"""
rest.py
This module contains functions to fetch news, weather, and currency data
from APIs and load project configuration from JSON.
"""

import requests
from .utils import open_json

config = open_json(None)

def fetch_news():
    """
    Fetch news articles from the API defined in config.json.
    Returns a list of dicts with keys: source, title, url, publishedAt, content.
    """
    try:
        api_url = config.get("news_api_url")
        if not api_url:
            raise KeyError("[ERROR] 'news_api_url' missing in config file.")

        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        data = res.json()

        articles = []
        for article in data.get("articles", []):
            articles.append({
                "source": article.get("source", {}).get("name"),
                "title": article.get("title"),
                "url": article.get("url"),
                "publishedAt": article.get("publishedAt"),
                "content": article.get("content")
            })

        print(f"[INFO] Fetched {len(articles)} news articles.")
        return articles

    except Exception as e:
        print(f"[ERROR] fetch_news() failed: {e}")
        return []

def get_location_from_ip():
    """
    Gets latitude and longitude of current IP using ipinfo.io API
    Returns:
        : latitude: float, longitude: float
    """
    res = requests.get("https://ipinfo.io",timeout=10)
    data = res.json()
    lat, lon = data["loc"].split(",")
    return float(lat), float(lon)

def fetch_weather():
    """
    Fetches current weather from the API defined in config.json.
    Returns:
        : Current weather details
    """
    try:
        details = open_json()
        latitude, longitude = get_location_from_ip()
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True
        }
        res = requests.get(details["weather_api_url"], params=params,timeout=10)
        data = res.json()
        current = data.get("current_weather", {})
        weather = []
        weather.append({
            "time": current.get("time"),
            "temperature": current.get("temperature"),
            "humidity": current.get("humidity")
        })
        return weather
    except Exception as e:
        print(f"fetch_weather failed {e}")
        return []

def get_location_from_ip():
    """Get latitude & longitude of current system using ipinfo.io."""
    try:
        res = requests.get("https://ipinfo.io", timeout=10)
        data = res.json()
        lat, lon = data.get("loc", "0,0").split(",")
        return float(lat), float(lon)
    except Exception as e:
        print(f"[ERROR] get_location_from_ip() failed: {e}")
        return 0.0, 0.0


def fetch_currency():
    """
    Fetch currency exchange rates from API.
    Returns list of dicts with base, target, and rate.
    """
    try:
        api_url = config.get("currency_api_url")
        if not api_url:
            raise KeyError("[ERROR] 'currency_api_url' missing in config file.")

        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        data = res.json()

        base = data.get("base_code")
        rates = data.get("rates", {})

        currency_list = [{
            "base": base,
            "target": target,
            "rate": rate
        } for target, rate in rates.items()]

        print(f"[INFO]  Fetched {len(currency_list)} currency rates.")
        return currency_list

    except Exception as e:
        print(f"[ERROR] fetch_currency() failed: {e}")
        return []
