import re
from src.jd_parser import JD_PARSED

# ─── helper ───────────────────────────────────────────────

def _normalize(val, lo=0.0, hi=1.0):
    return max(0.0, min(1.0, (val - lo) / (hi - lo + 1e-9)))


# ─── COMPONENT 1: Title Fit ────────────────────────────────
# Checks if current role is in the AI/ML/engineering space
# This is the primary honeypot trap killer

AI_TITLES = [
    "machine learning", "ml engineer", "ai engineer", "data scientist",
    "nlp engineer", "applied scientist", "research engineer",
    "software engineer", "backend engineer", "platform engineer",
    "search engineer", "ranking engineer", "recommendation",
    "data engineer", "full stack", "senior engineer",
]

BAD_TITLES = [
    "marketing", "sales", "hr manager", "operations manager",
    "content writer", "recruiter", "account manager",
    "business analyst", "product manager", "scrum master",
    "qa", "tester", "support", "finance", "legal",
]

def score_title(candidate: dict) -> float:
    title = candidate["profile"]["current_title"].lower()
    industry = candidate["profile"].get("current_industry", "").lower()

    # Hard disqualify on bad titles
    for bad in BAD_TITLES:
        if bad in title:
            return 0.05

    # Strong positive signal
    score = 0.3  # base
    for good in AI_TITLES:
        if good in title:
            score = 0.85
            break

    # Bonus for AI/tech industry
    if any(x in industry for x in ["technology", "software", "ai", "ml", "saas", "product"]):
        score = min(score + 0.1, 1.0)

    # Penalty for pure IT services (consulting)
    if any(x in industry for x in ["it services", "consulting", "outsourcing"]):
        score = max(score - 0.2, 0.0)

    return round(score, 4)


# ─── COMPONENT 2: Skill Quality Score ─────────────────────
# Not just "has skill" — endorsed + duration backed

def score_skills(candidate: dict) -> float:
    skills = candidate.get("skills", [])
    if not skills:
        return 0.0

    must_have = JD_PARSED["must_have_skills"]
    nice_to_have = JD_PARSED["nice_to_have_skills"]

    skill_names = {s["name"].lower() for s in skills}

    # Build a trust-weighted skill score
    total_score = 0.0
    max_possible = 0.0

    for skill in skills:
        name = skill["name"].lower()
        prof = skill.get("proficiency", "beginner")
        endorsements = skill.get("endorsements", 0)
        duration = skill.get("duration_months", 0)

        # Is this skill relevant?
        relevance = 0.0
        for mh in must_have:
            if mh in name or name in mh:
                relevance = 1.0
                break
        if relevance == 0.0:
            for nth in nice_to_have:
                if nth in name or name in nth:
                    relevance = 0.5
                    break

        if relevance == 0.0:
            continue

        # Proficiency weight
        prof_w = {"beginner": 0.2, "intermediate": 0.5,
                  "advanced": 0.8, "expert": 1.0}.get(prof, 0.3)

        # Trust multiplier: endorsements + duration
        # Keyword stuffer trap: high skill count but 0 endorsements & 0 duration
        endorse_w = min(endorsements / 20.0, 1.0)
        duration_w = min(duration / 24.0, 1.0)  # 24 months = full score
        trust = 0.5 + 0.25 * endorse_w + 0.25 * duration_w

        skill_score = relevance * prof_w * trust
        total_score += skill_score
        max_possible += relevance  # max if expert + fully trusted

    # Normalize
    if max_possible == 0:
        return 0.0

    # Bonus: assessment scores from Redrob platform
    assessments = candidate["redrob_signals"].get("skill_assessment_scores", {})
    assessment_bonus = 0.0
    for skill_name, score in assessments.items():
        for mh in must_have:
            if mh in skill_name.lower():
                assessment_bonus += score / 100.0 * 0.05
                break

    raw = total_score / max_possible
    return round(min(raw + assessment_bonus, 1.0), 4)


# ─── COMPONENT 3: Career Signal Score ─────────────────────
# Product company experience, no pure-consulting career

def score_career(candidate: dict) -> float:
    history = candidate.get("career_history", [])
    if not history:
        return 0.1

    disq_companies = JD_PARSED["disqualified_companies"]
    score = 0.5  # base

    product_company_months = 0
    consulting_months = 0
    ai_relevant_months = 0
    total_months = 0
    title_progression = []

    for job in history:
        company = job.get("company", "").lower()
        title = job.get("title", "").lower()
        industry = job.get("industry", "").lower()
        duration = job.get("duration_months", 0)
        company_size = job.get("company_size", "")
        desc = job.get("description", "").lower()
        total_months += duration

        # Consulting/services check
        is_consulting = any(d in company for d in disq_companies)
        if is_consulting or "it services" in industry or "consulting" in industry:
            consulting_months += duration
        else:
            product_company_months += duration

        # AI-relevant work check
        ai_keywords = ["embedding", "retrieval", "ranking", "recommendation",
                       "nlp", "ml", "machine learning", "search", "vector",
                       "model", "llm", "transformer", "rag", "fine-tun"]
        if any(kw in desc or kw in title for kw in ai_keywords):
            ai_relevant_months += duration

        title_progression.append(title)

    if total_months == 0:
        return 0.2

    # Penalty if entire career is consulting
    consulting_ratio = consulting_months / total_months
    if consulting_ratio > 0.8:
        score -= 0.3
    elif consulting_ratio > 0.5:
        score -= 0.15

    # Reward product company experience
    product_ratio = product_company_months / total_months
    score += product_ratio * 0.3

    # Reward AI-relevant work
    ai_ratio = ai_relevant_months / total_months
    score += ai_ratio * 0.25

    return round(max(0.0, min(1.0, score)), 4)


# ─── COMPONENT 4: Experience Fit ──────────────────────────
# 5-9 years ideal, but judgment-based (JD says so explicitly)

def score_experience(candidate: dict) -> float:
    yoe = candidate["profile"].get("years_of_experience", 0)
    ideal_min = JD_PARSED["experience_ideal_min"]  # 6
    ideal_max = JD_PARSED["experience_ideal_max"]  # 8
    hard_min = JD_PARSED["experience_min"]          # 5
    hard_max = JD_PARSED["experience_max"]          # 9

    if ideal_min <= yoe <= ideal_max:
        return 1.0
    elif hard_min <= yoe < ideal_min:
        return 0.75
    elif ideal_max < yoe <= hard_max:
        return 0.80
    elif hard_max < yoe <= 12:
        return 0.55  # Senior but overqualified
    elif 4 <= yoe < hard_min:
        return 0.60  # Slightly junior but possible
    elif yoe < 4:
        return 0.20  # Too junior
    else:
        return 0.30  # Very senior, probably wrong fit