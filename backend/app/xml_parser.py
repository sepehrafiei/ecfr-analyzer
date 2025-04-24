"""
XML parser for eCFR data files.
Processes XML files to extract section counts and word counts.
Handles hierarchical structure of eCFR documents.

Author: Sepehr Rafiei
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

# Absolute path to backend/data
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def get_section_and_word_count_by_structure(filename, structure):
    """
    filename: either 'title-1.xml' or a path containing it (e.g., 'data/titles/title-1.xml')
    structure: dict like {'title': 1, 'chapter': 'III', 'part': '425'}
    """
    try:
        # Sanitize filename in case user passes full or partial path
        clean_filename = Path(filename).name  # strips out folders, keeps only 'title-1.xml'
        file_path = DATA_DIR / "titles" / clean_filename

        logger.info(f"Processing XML file: {file_path}")

        if not file_path.exists():
            logger.warning(f"Missing XML file: {file_path}")
            return 0, 0

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.warning(f"Empty XML file: {file_path}")
            return 0, 0

        logger.info(f"Parsing XML file of size {file_size} bytes...")
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            logger.info("XML file parsed successfully")
        except ET.ParseError as e:
            logger.error(f"Error parsing XML file {file_path}: {str(e)}")
            return 0, 0

        tag_order = [('DIV1', 'title'), ('DIV3', 'chapter'), ('DIV5', 'part')]
        current_element = root

        for tag, key in tag_order:
            value = structure.get(key)
            if not value:
                continue
            logger.info(f"Looking for {tag} with value {value}")
            found = False
            for elem in current_element.iter(tag):
                if elem.attrib.get("N") == str(value):
                    current_element = elem
                    found = True
                    logger.info(f"Found matching {tag}")
                    break
            if not found:
                logger.warning(f"No matching {tag} found for value {value}")
                return 0, 0

        def count_words(elem, depth=0):
            if depth > 100:  # Prevent infinite recursion
                logger.warning("Maximum recursion depth reached in word counting")
                return 0
            try:
                count = len(elem.text.split()) if elem.text else 0
                for child in elem:
                    count += count_words(child, depth + 1)
                    if child.tail:
                        count += len(child.tail.split())
                return count
            except Exception as e:
                logger.error(f"Error counting words in element: {str(e)}")
                return 0

        logger.info("Counting sections and words...")
        try:
            section_count = sum(1 for _ in current_element.iter("DIV8"))
            word_count = count_words(current_element)
            logger.info(f"Found {section_count} sections and {word_count} words")
            return section_count, word_count
        except Exception as e:
            logger.error(f"Error counting sections/words: {str(e)}")
            return 0, 0
        
    except Exception as e:
        logger.error(f"Error processing XML file {filename}: {str(e)}")
        return 0, 0
