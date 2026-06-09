from datetime import date, datetime

def _days_since(date_str: str) -> int:
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days
    except:
        return 999

def score_behavioral(candidate: dict) -> float:
    s = candidate.get("redrob_signals", {})
    score = 0.0

    # 1. Is candidate actually available? (most important signal)
    if s.get("open_to_work_flag", False):
        score += 0.20

    # 2. Recency — last active (dead candidates must be down-ranked, JD says so)
    days_inactive = _days_since(s.get("last_active_date", "2000-01-01"))
    if days_inactive <= 7:
        score += 0.20
    elif days_inactive <= 30:
        score += 0.15
    elif days_inactive <= 60:
        score += 0.08
    elif days_inactive <= 180:
        score += 0.02
    else:
        score += 0.0  # 6+ months inactive → effectively unavailable

    # 3. Recruiter response rate
    rr = s.get("recruiter_response_rate", 0)
    score += rr * 0.15

    # 4. Notice period (JD: prefer sub-30 days)
    notice = s.get("notice_period_days", 90)
    if notice <= 30:
        score += 0.15
    elif notice <= 60:
        score += 0.08
    elif notice <= 90:
        score += 0.04
    else:
        score += 0.0

    # 5. Willing to relocate (role is Pune/Noida)
    location = candidate["profile"].get("location", "").lower()
    country = candidate["profile"].get("country", "").lower()
    preferred_locs = ["pune", "noida", "delhi", "ncr", "hyderabad",
                      "mumbai", "bangalore", "bengaluru", "gurgaon"]
    in_preferred = any(loc in location for loc in preferred_locs)
    in_india = "india" in country or any(loc in location for loc in preferred_locs)

    if in_preferred:
        score += 0.12
    elif in_india and s.get("willing_to_relocate", False):
        score += 0.08
    elif s.get("willing_to_relocate", False):
        score += 0.04

    # 6. Platform engagement (GitHub, verified, profile completeness)
    github = s.get("github_activity_score", -1)
    if github > 60:
        score += 0.08
    elif github > 30:
        score += 0.04

    completeness = s.get("profile_completeness_score", 0)
    score += (completeness / 100.0) * 0.05

    if s.get("verified_email") and s.get("verified_phone"):
        score += 0.03

    # 7. Interview reliability
    icr = s.get("interview_completion_rate", 0)
    score += icr * 0.02

    return round(min(score, 1.0), 4)