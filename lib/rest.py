# lib/rest.py

"""
rest.py
This module contains functions to fetch news, weather, and currency data
from APIs and load project configuration from JSON.
"""

import json
import os
import requests

# Determine config path relative to this file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
CONFIG_PATH = os.path.abspath(CONFIG_PATH)

def open_json():
    """
    Opens and loads the JSON configuration file.
    Returns:
         Configuration details from config.json
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_news():
    """
    Fetches news articles from the API defined in config.json.
    Returns:
         List of news articles
    """
    details = open_json()
    res = requests.get(details["news_api_url"],timeout=10)
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
    return articles

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

def fetch_currency():
    """
    Fetches currency exchange rates from the API defined in config.json.
    Returns:
         List of currency rates
    """
    details = open_json()
    res = requests.get(details["currency_api_url"],timeout=10)
    data = res.json()
    currency = []
    for target, rate in data.get("rates", {}).items():
        currency.append({
            "base": data.get("base_code"),
            "target": target,
            "rate": rate
        })
    return currency
