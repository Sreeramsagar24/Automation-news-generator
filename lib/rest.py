# lib/rest.py
import json
import requests

config_path = "/home/ubuntu/AUTOMATION_PROJECT/config/config.json"
def open_json():
    with open(config_path, 'r') as f:
        return json.load(f)

def fetch_news():
    details = open_json()
    res = requests.get(details["news_api_url"])
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
    res = requests.get("https://ipinfo.io")
    data = res.json()
    lat, lon = data["loc"].split(",")
    return float(lat), float(lon)

def fetch_weather():
    details = open_json()
    latitude, longitude = get_location_from_ip()
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True
    }
    res = requests.get(details["weather_api_url"], params=params)
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
    details = open_json()
    res = requests.get(details["currency_api_url"])
    data = res.json()
    currency = []
    for target, rate in data.get("rates", {}).items():
        currency.append({
            "base": data.get("base_code"),
            "target": target,
            "rate": rate
        })
    return currency
