"""
Configuration module for the eCFR Analyzer.
Manages environment variables and API request headers.
Handles base directory paths and environment loading.

Author: Sepehr Rafiei
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env", override=True)

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "eCFRAnalyzer/1.0"
}
