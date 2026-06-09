from datetime import date, datetime

def _days_since(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days
    except:
        return 999

def generate_reasoning(ranked: dict) -> str:
    c = ranked["_candidate"]
    p = c["profile"]
    s = c["redrob_signals"]
    breakdown = ranked["breakdown"]
    rank = ranked["rank"]

    name_placeholder = p.get("current_title", "Candidate")
    yoe = p.get("years_of_experience", 0)
    location = p.get("location", "Unknown")
    notice = s.get("notice_period_days", "?")
    last_active_days = _days_since(s.get("last_active_date", "2000-01-01"))
    response_rate = s.get("recruiter_response_rate", 0)
    open_to_work = s.get("open_to_work_flag", False)

    # Build specific reasoning — no templates, actual facts
    parts = []

    # Title + YoE fact
    parts.append(f"{name_placeholder} with {yoe:.1f} yrs experience based in {location}.")

    # Skill insight
    if breakdown["skills"] >= 0.65:
        parts.append("Strong endorsed AI/retrieval skills backed by platform assessments.")
    elif breakdown["skills"] >= 0.40:
        parts.append("Moderate skill match — some relevant AI/ML skills present.")
    else:
        parts.append("Limited match on core retrieval/ranking skills required.")

    # Career insight
    if breakdown["career"] >= 0.65:
        parts.append("Career shows product-company experience with AI-relevant work.")
    elif breakdown["career"] < 0.35:
        parts.append("Career mostly in IT services/consulting — concern per JD criteria.")

    # Behavioral insight
    if last_active_days > 180:
        parts.append(f"Caution: last active {last_active_days} days ago — availability uncertain.")
    elif not open_to_work:
        parts.append("Not marked open-to-work — outreach may be needed.")
    else:
        parts.append(f"Actively available; recruiter response rate {response_rate:.0%}.")

    # Notice period
    if notice <= 30:
        parts.append(f"Notice period {notice}d — fits JD preference.")
    elif notice > 90:
        parts.append(f"Notice period {notice}d — longer than preferred.")

    reasoning = " ".join(parts)
    # Trim to reasonable length
    return reasoning[:280]