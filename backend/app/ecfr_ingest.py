import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path, override=True)

API_BASE = os.getenv("ECFR_API_BASE")
DATA_VERSION = os.getenv("DATA_VERSION")
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "eCFRAnalyzer/1.0"
}


def fetch_agencies():
     url = "https://www.ecfr.gov/api/admin/v1/agencies.json"
     try:
         res = requests.get(url, headers=HEADERS)
         res.raise_for_status()
         data = res.json()
         os.makedirs("data/agencies", exist_ok=True)
         with open(f"data/agencies/agencies.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

         print(f"Saved structure to data/agencies.json")
         return data
         

     except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

     except Exception as e:
        print(f"Unexpected error: {e}")

def get_agency_scope_map(path="data/agencies/agencies.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            agencies = json.load(f)["agencies"]

   
        agency_scope = {}
        for agency in agencies:
            refs = agency.get("cfr_references", [])
            if refs:
                agency_scope[agency["name"]] = refs

        return agency_scope

    except Exception as e:
        print(f"Failed to load agency mapping: {e}")
        return {}




def get_section_and_word_count_by_structure(path, structure):
    tree = ET.parse(path)
    root = tree.getroot()

    tag_order = [('DIV1', 'title'), ('DIV3', 'chapter'), ('DIV5', 'part')]
    current_element = root

    # Navigate to the deepest specified level
    for tag, key in tag_order:
        value = structure.get(key)
        if value is None:
            continue
        found = False
        for elem in current_element.iter(tag):
            if elem.attrib.get("N") == str(value):
                current_element = elem
                found = True
                break
        if not found:
            return 0, 0  # If any level doesn't match, return zero counts

    def count_words(elem):
        count = 0
        if elem.text:
            count += len(elem.text.split())
        for child in elem:
            count += count_words(child)
            if child.tail:
                count += len(child.tail.split())
        return count

    section_count = sum(1 for _ in current_element.iter("DIV8"))
    word_count = count_words(current_element)

    return section_count, word_count




def fetch_latest_title_dates():
    url = "https://www.ecfr.gov/api/versioner/v1/titles.json"
    try:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        data = res.json()
        latest_date = {}
        titles = data['titles']
        for title in titles:
            latest_date[title["number"]] = title["latest_amended_on"]
        return latest_date
    except Exception as e:
        print(f"Failed to fetch latest date: {e}")
    return None


def fetch_all_titles():
    dates = fetch_latest_title_dates()
    os.makedirs("data/titles", exist_ok=True)

    for title, date in dates.items():
        url = f'https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml'
        try:
            response = requests.get(url)
            response.raise_for_status()
            file_path = f"data/titles/title-{title}.xml"
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Saved: {file_path}")
        except requests.RequestException as e:
            print(f"Failed to fetch title {title}: {e}")


def get_agency_data():
    scope_map = get_agency_scope_map()
    agency_dict = {}
    for agency, deps in scope_map.items():
        sections = 0
        words = 0
        for dep in deps:
            print(dep)
            title = dep['title']
            section_count, word_count = get_section_and_word_count_by_structure(f'data/titles/title-{title}.xml', dep)
            sections += section_count
            words += word_count
        agency_dict[agency] = (sections, words)
    return agency_dict


if __name__ == "__main__":
    # Test with a known populated section
    #fetch_agencies()
    #print(get_agency_scope_map())
    # parse_xlm()
    # fetch_all_titles()
    print(get_agency_data())
    


# def get_title_structure(title_number: int, date: str = DATA_VERSION):
#     url = f"{API_BASE}/structure/{date}/title-{title_number}.json"
#     print(f"Fetching Title {title_number} structure from {url}")
    
#     try:
#         res = requests.get(url, headers=HEADERS)
#         res.raise_for_status()
#         data = res.json()

#         os.makedirs("data", exist_ok=True)
#         with open(f"data/structure_title_{title_number}.json", "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=2)

#         print(f"Saved structure to data/structure_title_{title_number}.json")
#         return data

#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")
#     except Exception as e:
#         print(f"Unexpected error: {e}")


# def extract_parts_with_sections(structure_data):
#     parts = []

#     def walk(node):
#         if node["type"] == "part":
#             part = {
#                 "part_number": node["identifier"],
#                 "part_label": node["label"],
#                 "sections": []
#             }
#             if "children" in node:
#                 for child in node["children"]:
#                     if child["type"] == "section":
#                         part["sections"].append({
#                             "section_number": child["identifier"],
#                             "label": child["label"]
#                         })
#             parts.append(part)
#         if "children" in node:
#             for child in node["children"]:
#                 walk(child)

#     walk(structure_data)
#     return parts






# def fetch_section_text(title: str, part: str, section: str, date: str = DATA_VERSION):
#     url = f"{API_BASE}/full/{date}/title-{title}.xml?part={part}&section={section}"
#     print(f"Fetching Section {section} from {url}")
    
#     try:
#         res = requests.get(url, headers=HEADERS)
#         res.raise_for_status()
#         xml_content = res.content

#         root = ET.fromstring(xml_content)
#         text_nodes = root.findall(".//P")
#         text = "\n\n".join(p.text.strip() for p in text_nodes if p.text)

#         out_dir = f"data/sections/title-{title}"
#         os.makedirs(out_dir, exist_ok=True)
#         out_path = f"{out_dir}/section-{section}.json"
#         with open(out_path, "w", encoding="utf-8") as f:
#             json.dump({
#                 "title": title,
#                 "part": part,
#                 "section": section,
#                 "text": text
#             }, f, indent=2)

#         print(f"Saved section text to {out_path}")
#         return text

#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")
#     except ET.ParseError as e:
#         print(f"XML parsing failed: {e}")
#     except Exception as e:
#         print(f"Unexpected error: {e}")