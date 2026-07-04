"""
MindShift Extra Case Studies — 55 new NLP cases
Loads from seed_cases_extra.json to avoid Python quoting issues.
"""

import json
import os


def get_extra_cases():
    """Return the 55 extra NLP case studies to be merged with the existing 5."""
    json_path = os.path.join(os.path.dirname(__file__), "seed_cases_extra.json")
    with open(json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
    return cases
