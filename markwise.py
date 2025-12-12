"""
MarkWise prototype
- Input: song title, lyrics text, or book title
- Uses modular API clients (placeholders) to fetch potential matches
- Computes similarity scores and overlapping highlights
- Produces an HTML report (exportable)
"""

import urllib.parse, urllib.request, urllib.error, json
import requests
import os
import base64
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def safe_get(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=10) #10 seconds before it quits
        response.raise_for_status() # check if successful, ir errors occur raise an exception
        return response.json() #json to dictionary
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Lowercase and remove punctuation
def normalize(text):
    import re
    return re.sub(r"[^\w\s]", "", (text or "").lower())

# Highlight exact words in text that appear in query
def highlight_overlap(query, text):
    query_words = normalize(query).split()
    words = text.split()
    highlighted_words = []
    for w in words:
        if normalize(w) in query_words:
            highlighted_words.append(f"<mark>{w}</mark>")
        else:
            highlighted_words.append(w)
    return " ".join(highlighted_words)

# Highlight words in text that partially match query words
def highlight_partial(query, text, threshold=0.7):
    query_words = normalize(query).split()
    words = text.split()
    highlighted_words = []

    for w in words:
        nw = normalize(w)
        match_found = any(SequenceMatcher(None, nw, q).ratio() > threshold for q in query_words)
        if match_found:
            highlighted_words.append(f"<mark>{w}</mark>")
        else:
            highlighted_words.append(w)
    return " ".join(highlighted_words)

def search_books(title, max_results=5):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"intitle:{title}", "maxResults": max_results}
    data = safe_get(base_url, params)
    return data.get("items", []) if data else [] # return a list of findings

# Convert raw Google Books API results into a list of dictionaries
# with similarity scores and highlighted matches for the Flask app
def process_books_for_display(results, query):
    processed = []
    for book in results:
        info = book.get("volumeInfo", {})
        title = info.get("title", "")
        authors = ", ".join(info.get("authors", ["Unknown"]))
        preview_link = info.get("previewLink", "#")

        # Simple similarity using SequenceMatcher
        similarity = round(SequenceMatcher(None, query.lower(), title.lower()).ratio() * 100, 2)
        highlighted = highlight_overlap(query, title)

        processed.append({
            "title": title,
            "authors": authors,
            "infoLink": preview_link,
            "similarity": similarity,
            "highlight": highlighted
        })
    return processed

# this method written by ai
def get_spotify_token():
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth}"}
    data = {"grant_type": "client_credentials"}
    r = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

# search Spotify tracks
def search_spotify(query, limit=5):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": limit}
    r = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    r.raise_for_status()
    items = r.json().get("tracks", {}).get("items", [])
    results = []
    for it in items:
        results.append({
            "title": it["name"],
            "artists": ", ".join([a["name"] for a in it["artists"]]),
            "spotify_url": it["external_urls"]["spotify"]
        })
    return results

# Convert raw Spotify API results into a list of dicts with similarity and highlights
def process_spotify_for_display(results, query):
    processed = []
    for track in results:
        title = track["title"]
        artists = track["artists"]
        url = track["spotify_url"]

        similarity = round(SequenceMatcher(None, query.lower(), title.lower()).ratio() * 100, 2)
        highlighted = highlight_partial(query, title)  # partial word match for lyrics/songs

        processed.append({
            "title": title,
            "artists": artists,
            "spotify_url": url,
            "similarity": similarity,
            "highlight": highlighted
        })
    return processed
