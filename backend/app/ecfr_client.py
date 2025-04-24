"""
Client for interacting with the eCFR API.
Handles data fetching, caching, and agency scope mapping.
Implements retry logic and error handling for API requests.

Author: Sepehr Rafiei
"""

from pathlib import Path
import os
import json
import requests
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime, timedelta

from .config import HEADERS

logger = logging.getLogger(__name__)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_with_retry(url, headers=None):
    """Fetch data from URL with retries."""
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        raise

def fetch_and_cache(url, rel_path, max_age_hours=24):
    """Fetch and cache data with age checking."""
    full_path = DATA_DIR / rel_path
    
    # Check if cached file exists and is recent enough
    if full_path.exists():
        file_age = datetime.now() - datetime.fromtimestamp(full_path.stat().st_mtime)
        if file_age < timedelta(hours=max_age_hours):
            logger.info(f"Using cached data from {rel_path}")
            with open(full_path, 'r') as f:
                return json.load(f)
    
    logger.info(f"Fetching fresh data from {url}")
    res = fetch_with_retry(url, headers=HEADERS)
    data = res.json()

    # Ensure directory exists
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to cache
    with open(full_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return data

def extract_all_refs(agency):
    """Recursively get all cfr_references from an agency and its children."""
    refs = agency.get("cfr_references", [])
    for child in agency.get("children", []):
        refs.extend(extract_all_refs(child))
    return refs

def get_agency_scope_map():
    """Get agency scope mapping with error handling."""
    try:
        data = fetch_and_cache(
            "https://www.ecfr.gov/api/admin/v1/agencies.json",
            "agencies/agencies.json"
        )
        
        agency_scope = {}
        for agency in data["agencies"]:
            refs = extract_all_refs(agency)
            if refs:
                agency_scope[agency["name"]] = refs
        return agency_scope
    except Exception as e:
        logger.error(f"Error getting agency scope map: {str(e)}")
        raise

def ensure_titles_downloaded():
    """Ensure all titles are downloaded with proper error handling."""
    try:
        meta = fetch_and_cache(
            "https://www.ecfr.gov/api/versioner/v1/titles.json",
            "titles_meta.json"
        )

        for t in meta["titles"]:
            title_num = t["number"]
            date = t["latest_amended_on"]
            path = DATA_DIR / f"titles/title-{title_num}.xml"
            
            # Check if we need to download or update the file
            if not path.exists() or (
                datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
            ) > timedelta(hours=24):
                logger.info(f"Downloading title {title_num}")
                url = f'https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title_num}.xml'
                res = fetch_with_retry(url, headers=HEADERS)
                
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'wb') as f:
                    f.write(res.content)
                logger.info(f"Successfully downloaded title {title_num}")
            else:
                logger.debug(f"Title {title_num} is up to date")
                
    except Exception as e:
        logger.error(f"Error ensuring titles are downloaded: {str(e)}")
        raise
