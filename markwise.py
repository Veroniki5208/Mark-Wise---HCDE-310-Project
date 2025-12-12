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

def search_books(title, max_results=5):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"intitle:{title}", "maxResults": max_results}
    data = safe_get(base_url, params)
    return data.get("items", []) if data else [] # return a list of findings

def print_book_info(results, title):
    if not results:
        print(f"No books found for '{title}'.\n")
        return
    print(f"Top results for '{title}':")
    for book in results:
        info = book.get("volumeInfo", {})
        print(f"  - Title: {info.get('title', 'N/A')}")
        print(f"    Author(s): {', '.join(info.get('authors', ['Unknown']))}") # combine into string all authors if missing -> Unknown
        print(f"    Publisher: {info.get('publisher', 'N/A')}")
        print(f"    Published: {info.get('publishedDate', 'N/A')}")
        print(f"    Preview: {info.get('previewLink', 'N/A')}") # link to book, for double checking manually by user
        print()

def main():
    print("Google Books Title Checker")
    mode = input("Enter 'list' to check a preset list or 'manual' to enter your own titles: ").strip().lower()

    if mode == "list":
        titles = ["The Hobbit", "Frankenstein", "Divergent", "To Kill a Mockingbird"]
    else:
        titles = input("Enter book titles separated by commas: ").split(",")

    for title in [t.strip() for t in titles]: # t.strip - remove extra spaces
        results = search_books(title)
        print_book_info(results, title)

if __name__ == "__main__":
    main()