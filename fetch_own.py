"""
Stahuje followers_count pro vlastní (spravované) IG Business/Creator účty
přes oficiální Meta Graph API. Zdarma, stabilní, žádné riziko banu.

Předpoklad: účet je propojen s Facebook stránkou a máte platný access token
s oprávněním instagram_basic (viz README.md).
"""
import requests

GRAPH_API_VERSION = "v19.0"


def fetch_own_followers(ig_user_id: str, access_token: str) -> int:
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{ig_user_id}"
    params = {"fields": "followers_count", "access_token": access_token}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if "followers_count" not in data:
        raise ValueError(f"Neočekávaná odpověď Graph API: {data}")
    return data["followers_count"]
