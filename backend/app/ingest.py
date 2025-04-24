"""
Data ingestion module for the eCFR Analyzer.
Handles downloading and processing of eCFR data, including agency metrics.
Manages database updates and data refresh operations.

Author: Sepehr Rafiei
"""

from .ecfr_client import get_agency_scope_map, ensure_titles_downloaded
from .xml_parser import get_section_and_word_count_by_structure
from .db import SessionLocal, AgencyMetrics

def run_ingestion():
    ensure_titles_downloaded()
    agency_map = get_agency_scope_map()
    session = SessionLocal()

    for name, refs in agency_map.items():
        section_total = 0
        word_total = 0

        for ref in refs:
            title = ref['title']
            file_path = f"data/titles/title-{title}.xml"
            section_count, word_count = get_section_and_word_count_by_structure(file_path, ref)
            section_total += section_count
            word_total += word_count

        existing = session.query(AgencyMetrics).filter_by(name=name).first()
        if existing:
            existing.scope = refs
            existing.section_count = section_total
            existing.word_count = word_total
        else:
            new = AgencyMetrics(
                name=name,
                scope=refs,
                section_count=section_total,
                word_count=word_total
            )
            session.add(new)

    session.commit()
    session.close()


def refresh_all_data():
    print("Refreshing agencies and titles from API...")
    ensure_titles_downloaded()
    run_ingestion()
    print("Refresh complete.")