from __future__ import annotations

import hashlib
from typing import Optional

# Predefined experiments with variants
EXPERIMENTS: dict[str, dict[str, object]] = {
    "onboarding_pages": {
        "name": "onboarding_pages",
        "description": "Onboarding flow page count",
        "variants": ["5_pages", "3_pages_simplified"],
    },
    "pricing_default": {
        "name": "pricing_default",
        "description": "Default pricing tab shown to new users",
        "variants": ["monthly", "annually"],
    },
    "membership_popup_timing": {
        "name": "membership_popup_timing",
        "description": "When to show the membership upgrade popup",
        "variants": ["on_app_open", "on_feature_lock"],
    },
}


def get_experiment(user_id: str, experiment_name: str) -> Optional[str]:
    """
    Assign a user to an experiment variant using simple hash-based assignment.

    Returns None if the experiment is not defined.
    Uses SHA256 hash of (user_id + experiment_name) for deterministic but
    evenly distributed assignment.
    """
    experiment = EXPERIMENTS.get(experiment_name)
    if not experiment:
        return None

    variants = experiment["variants"]
    hash_input = f"{user_id}:{experiment_name}"
    hash_bytes = hashlib.sha256(hash_input.encode()).digest()
    # Use first 4 bytes as an integer and mod by number of variants
    hash_int = int.from_bytes(hash_bytes[:4], byteorder="big")
    variant_index = hash_int % len(variants)
    return variants[variant_index]  # type: ignore[no-any-return]
