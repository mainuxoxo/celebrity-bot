import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from transformers import pipeline

# Cache for previous search queries
cache = {}

# Optional alias mapping
alias_map = {
    "The Rock": "Dwayne Johnson",
    "Drake": "Aubrey Graham"
}

# Set up Hugging Face NER pipeline
ner = pipeline("ner", grouped_entities=True)

def extract_ner(text):
    """
    Extracts named entities (people, locations, miscellaneous) from a given text.
    """
    entities = ner(text)
    return [e['word'] for e in entities if e['entity_group'] in ["PER", "LOC", "MISC"]]

def normalize_query(name, nationality=None, occupation=None):
    """
    Combines name, nationality, and occupation into a single query string.
    Applies alias mapping if available.
    """
    name = alias_map.get(name.strip(), name.strip())
    parts = [name, nationality or "", occupation or "", "official social media"]
    return " ".join(filter(None, parts))

def search_links(query):
    """
    Uses DuckDuckGo search to find social media links for a given query.
    Filters for major platforms including X, Snapchat, and OnlyFans.
    """
    if query in cache:
        return cache[query]

    # Add more platforms here as needed
    platforms = [
        "instagram.com", "twitter.com", "facebook.com",
        "tiktok.com", "youtube.com", "linkedin.com",
        "snapchat.com", "x.com", "onlyfans.com"
    ]

    links = []
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=15)
        for result in results:
            url = result.get("href")
            if url and any(platform in url for platform in platforms):
                links.append(url)

    cache[query] = links
    return links

