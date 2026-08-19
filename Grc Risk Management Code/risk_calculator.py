"""
GRC Risk Register - Qualitative Risk Calculation Engine
Deterministic 3x3 Likelihood x Impact Qualitative Risk Matrix
Standard: NIST SP 800-30 Rev 1 / ISO 27005:2022
"""

from typing import Tuple, Dict, Any

# Likelihood Definitions (1 to 3)
LIKELIHOOD_LABELS = {
    1: "Low (Unlikely)",
    2: "Medium (Possible)",
    3: "High (Probable)"
}

# Impact Definitions (1 to 3)
IMPACT_LABELS = {
    1: "Low (Minor Impact)",
    2: "Medium (Moderate Impact)",
    3: "High (Severe Impact)"
}

# Risk Level Classification Rules:
# Score 1 - 2 : Low
# Score 3 - 4 : Medium
# Score 6 - 9 : High
RISK_LEVEL_CONFIG = {
    "Low": {
        "min_score": 1,
        "max_score": 2,
        "color": "#10b981",       # Emerald Green
        "bg_color": "rgba(16, 185, 129, 0.15)",
        "badge_class": "badge-low",
        "action_guidance": "Acceptable risk. Monitor periodically."
    },
    "Medium": {
        "min_score": 3,
        "max_score": 4,
        "color": "#f59e0b",       # Amber Orange
        "bg_color": "rgba(245, 158, 11, 0.15)",
        "badge_class": "badge-medium",
        "action_guidance": "Moderate risk. Plan mitigation and assign monitoring."
    },
    "High": {
        "min_score": 6,
        "max_score": 9,
        "color": "#ef4444",       # Crimson Red
        "bg_color": "rgba(239, 68, 68, 0.15)",
        "badge_class": "badge-high",
        "action_guidance": "Critical / High risk. Immediate treatment and senior review required."
    }
}


def calculate_risk(likelihood: int, impact: int) -> Dict[str, Any]:
    """
    Calculates the deterministic qualitative risk score and level.
    
    Formula: Risk Score = Likelihood * Impact
    
    Bounds:
        Likelihood: [1, 2, 3]
        Impact:     [1, 2, 3]
        Score:      [1, 9]
        Level:      Low (1-2), Medium (3-4), High (6-9)
    """
    if not isinstance(likelihood, int) or not isinstance(impact, int):
        try:
            likelihood = int(likelihood)
            impact = int(impact)
        except (ValueError, TypeError):
            raise ValueError("Likelihood and Impact must be valid integers between 1 and 3.")

    if likelihood < 1 or likelihood > 3:
        raise ValueError(f"Likelihood value {likelihood} is out of bounds. Must be 1, 2, or 3.")
    
    if impact < 1 or impact > 3:
        raise ValueError(f"Impact value {impact} is out of bounds. Must be 1, 2, or 3.")

    score = likelihood * impact

    if score <= 2:
        level = "Low"
    elif score <= 4:
        level = "Medium"
    else:
        level = "High"

    config = RISK_LEVEL_CONFIG[level]

    return {
        "likelihood": likelihood,
        "likelihood_label": LIKELIHOOD_LABELS[likelihood],
        "impact": impact,
        "impact_label": IMPACT_LABELS[impact],
        "score": score,
        "level": level,
        "color": config["color"],
        "bg_color": config["bg_color"],
        "badge_class": config["badge_class"],
        "guidance": config["action_guidance"]
    }


def get_matrix_definition() -> Dict[str, Any]:
    """Returns the full 3x3 qualitative matrix structure for visualization."""
    matrix = []
    for l in [3, 2, 1]:  # High to Low on Y-axis
        row = []
        for i in [1, 2, 3]:  # Low to High on X-axis
            res = calculate_risk(l, i)
            row.append(res)
        matrix.append(row)
    return {
        "matrix": matrix,
        "likelihood_labels": LIKELIHOOD_LABELS,
        "impact_labels": IMPACT_LABELS,
        "levels": RISK_LEVEL_CONFIG
    }
