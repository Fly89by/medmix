SCORE_MAP = {
    "industry": {
        "construction": 25,
        "real estate": 25,
        "engineering": 20,
        "government": 20,
        "manufacturing": 15,
        "retail": 10,
    },
    "source": {
        "website": 10,
        "referral": 20,
        "social_media": 10,
        "direct": 15,
        "manual": 5,
    },
    "city_medina": 15,
}


def calculate_lead_score(industry: str = None, city: str = None, source: str = None) -> int:
    score = 10
    if industry:
        industry_lower = industry.lower()
        for key, val in SCORE_MAP["industry"].items():
            if key in industry_lower:
                score += val
                break
        else:
            score += 5

    if source:
        source_lower = source.lower()
        score += SCORE_MAP["source"].get(source_lower, 5)

    if city and "medina" in city.lower():
        score += SCORE_MAP["city_medina"]

    return min(score, 100)
