"""
Data ingestion module for the eCFR Analyzer.
Handles downloading and processing of eCFR data, including agency metrics.
Manages database updates and data refresh operations.

Author: Sepehr Rafiei
"""

from .ecfr_client import get_agency_scope_map, ensure_titles_downloaded
from .xml_parser import get_section_and_word_count_by_structure
from .db import SessionLocal, AgencyMetrics
import logging
from datetime import datetime, timedelta
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# Cache for XML parsing results
xml_cache = {}

def run_ingestion():
    """Run data ingestion with proper error handling and timeouts."""
    session = None
    try:
        logger.info("Starting data ingestion process...")
        
        # First ensure we have the latest titles
        logger.info("Ensuring titles are downloaded...")
        ensure_titles_downloaded()
        logger.info("Titles download complete")
        
        # Get agency map
        logger.info("Fetching agency scope map...")
        agency_map = get_agency_scope_map()
        logger.info(f"Found {len(agency_map)} agencies to process")
        
        session = SessionLocal()
        
        # Process all agencies
        for name, refs in agency_map.items():
            try:
                logger.info(f"Processing agency: {name}")
                section_total = 0
                word_total = 0
                processed_refs = 0
                skipped_refs = 0
                
                # Process each reference for the agency
                for ref in refs:
                    try:
                        title = ref['title']
                        logger.info(f"Processing title {title} for agency {name}")
                        file_path = f"data/titles/title-{title}.xml"
                        
                        # Skip title 35 as it's missing
                        if title == 35:
                            logger.warning("Skipping title 35 as it's missing")
                            skipped_refs += 1
                            continue
                            
                        # Check if file exists
                        if not Path(file_path).exists():
                            logger.warning(f"Missing file for title {title}, skipping...")
                            skipped_refs += 1
                            continue
                        
                        # Check cache first
                        cache_key = f"{title}_{ref.get('chapter', '')}_{ref.get('part', '')}"
                        if cache_key in xml_cache:
                            section_count, word_count = xml_cache[cache_key]
                            logger.info(f"Using cached results for title {title}")
                        else:
                            section_count, word_count = get_section_and_word_count_by_structure(file_path, ref)
                            xml_cache[cache_key] = (section_count, word_count)
                            
                        section_total += section_count
                        word_total += word_count
                        processed_refs += 1
                        logger.info(f"Title {title} processed: {section_count} sections, {word_count} words")
                    except Exception as e:
                        logger.error(f"Error processing reference {ref} for agency {name}: {str(e)}")
                        skipped_refs += 1
                        continue
                
                logger.info(f"Agency {name} processed: {processed_refs} references processed, {skipped_refs} skipped")
                
                # Update or create agency metrics
                existing = session.query(AgencyMetrics).filter_by(name=name).first()
                if existing:
                    logger.info(f"Updating existing agency: {name}")
                    existing.scope = refs
                    existing.section_count = section_total
                    existing.word_count = word_total
                    existing.updated_at = datetime.now()
                else:
                    logger.info(f"Creating new agency: {name}")
                    new = AgencyMetrics(
                        name=name,
                        scope=refs,
                        section_count=section_total,
                        word_count=word_total,
                        updated_at=datetime.now()
                    )
                    session.add(new)
                
                # Commit after each agency to prevent long transactions
                session.commit()
                logger.info(f"Successfully processed agency: {name}")
                
            except Exception as e:
                logger.error(f"Error processing agency {name}: {str(e)}")
                session.rollback()
                continue
            
        logger.info("Data ingestion process completed successfully")
            
    except Exception as e:
        logger.error(f"Error in run_ingestion: {str(e)}")
        if session:
            session.rollback()
    finally:
        if session:
            session.close()
            logger.info("Database session closed")

def refresh_all_data():
    """Refresh all data with proper error handling."""
    try:
        logger.info("Starting data refresh process...")
        run_ingestion()
        logger.info("Data refresh completed successfully")
    except Exception as e:
        logger.error(f"Error during refresh: {str(e)}")
        # Don't raise the exception, allow the app to continue
        pass