"""
XML parser for eCFR data files.
Processes XML files to extract section counts and word counts.
Handles hierarchical structure of eCFR documents.

Author: Sepehr Rafiei
"""

import xml.etree.ElementTree as ET
from pathlib import Path

# Absolute path to backend/data
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def get_section_and_word_count_by_structure(filename, structure):
    """
    filename: either 'title-1.xml' or a path containing it (e.g., 'data/titles/title-1.xml')
    structure: dict like {'title': 1, 'chapter': 'III', 'part': '425'}
    """
    # Sanitize filename in case user passes full or partial path
    clean_filename = Path(filename).name  # strips out folders, keeps only 'title-1.xml'
    file_path = DATA_DIR / "titles" / clean_filename

    if not file_path.exists():
        print(f"Missing XML file: {file_path}")
        return 0, 0

    tree = ET.parse(file_path)
    root = tree.getroot()

    tag_order = [('DIV1', 'title'), ('DIV3', 'chapter'), ('DIV5', 'part')]
    current_element = root

    for tag, key in tag_order:
        value = structure.get(key)
        if not value:
            continue
        found = False
        for elem in current_element.iter(tag):
            if elem.attrib.get("N") == str(value):
                current_element = elem
                found = True
                break
        if not found:
            return 0, 0

    def count_words(elem):
        count = len(elem.text.split()) if elem.text else 0
        for child in elem:
            count += count_words(child)
            if child.tail:
                count += len(child.tail.split())
        return count

    section_count = sum(1 for _ in current_element.iter("DIV8"))
    word_count = count_words(current_element)

    return section_count, word_count
