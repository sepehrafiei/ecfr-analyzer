"""
Analysis module for the eCFR Analyzer.
Provides functions for analyzing agency metrics and generating insights.
Includes methods for calculating averages and retrieving agency summaries.

Author: Sepehr Rafiei
"""

from sqlalchemy.orm import Session
from .db import AgencyMetrics

def get_top_agencies_by_word_count(session: Session, limit=10):
    return (
        session.query(AgencyMetrics)
        .order_by(AgencyMetrics.word_count.desc())
        .limit(limit)
        .all()
    )

def get_average_section_length(session: Session):
    agencies = session.query(AgencyMetrics).all()
    total_words = sum(a.word_count for a in agencies)
    total_sections = sum(a.section_count for a in agencies)
    return total_words / total_sections if total_sections else 0

def get_agency_summary(session: Session, agency_name: str):
    return session.query(AgencyMetrics).filter_by(name=agency_name).first()
