def calculate_score(match_result: dict) -> float:
    """
    V1 legacy score calculation.
    Fixed key lookup: 'matched' instead of 'match' to prevent KeyError.
    For V2 hybrid scoring, use src.matching.hybrid_matcher.hybrid_match instead.
    """
    skill_pct = match_result.get("skills", {}).get("match_percentage", 0.0)
    exp_info = match_result.get("experience", {})

    # Handle boolean or numeric score in experience
    if "score" in exp_info:
        exp_score = exp_info["score"]
    else:
        exp_score = 100.0 if exp_info.get("matched", False) else 0.0

    score = (skill_pct * 0.8) + (exp_score * 0.2)
    return round(score, 1)