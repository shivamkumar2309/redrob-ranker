from datetime import date, datetime

# ── JD Configuration ─────────────────────────────────────────
JD_PARSED = {
    "experience_ideal_min": 6,
    "experience_ideal_max": 8,
    "experience_min": 5,
    "experience_max": 9,
    "must_have_skills": [
        "embeddings", "sentence-transformers", "vector database",
        "faiss", "pinecone", "weaviate", "qdrant", "milvus",
        "elasticsearch", "opensearch", "semantic search",
        "retrieval", "ranking", "recommendation", "RAG",
        "NDCG", "MRR", "MAP", "evaluation", "A/B testing",
        "python", "NLP", "information retrieval",
        "hybrid search", "dense retrieval", "BM25",
    ],
    "nice_to_have_skills": [
        "fine-tuning", "LoRA", "QLoRA", "PEFT",
        "learning-to-rank", "XGBoost", "LLM",
        "distributed systems", "open-source",
    ],
    "disqualified_companies": [
        "tcs", "infosys", "wipro", "accenture",
        "cognizant", "capgemini", "mindtree", "mphasis",
        "hexaware", "tech mahindra"
    ],
}

WEIGHTS = {
    "title": 0.25,
    "skills": 0.25,
    "career": 0.20,
    "experience": 0.15,
    "behavioral": 0.15,
}

# ── Title Lists ───────────────────────────────────────────────
STRONG_AI_TITLES = [
    "machine learning engineer", "ml engineer", "ai engineer",
    "nlp engineer", "applied scientist", "research engineer",
    "search engineer", "ranking engineer", "recommendation systems",
    "senior ml", "senior ai", "senior nlp", "senior machine learning",
    "applied ml", "applied ai",
]
ACCEPTABLE_TITLES = [
    "data scientist", "software engineer", "backend engineer",
    "platform engineer", "data engineer", "full stack engineer",
    "senior software engineer", "senior data scientist", "senior engineer",
]
WEAK_TITLES = [
    "java developer", "frontend engineer", "full stack developer",
    "cloud engineer", "devops", "android", "ios developer",
    "mobile developer", "web developer", "php developer",
    "frontend developer", "full-stack",
]
BAD_TITLES = [
    "marketing", "sales", "hr manager", "operations manager",
    "content writer", "recruiter", "account manager",
    "business analyst", "product manager", "scrum master",
    "qa engineer", "tester", "support", "finance", "legal",
    "mechanical engineer", "civil engineer", "electrical engineer",
    "graphic designer", "ui designer", "ux designer",
    "customer success", "project manager",
]

# ── AI job roles for career scoring ──────────────────────────
AI_ROLE_TITLES = [
    "ml engineer", "machine learning", "ai engineer", "nlp",
    "data scientist", "search engineer", "ranking engineer",
    "recommendation", "research engineer", "applied scientist",
    "backend engineer", "software engineer", "platform engineer",
]

# ── Scoring Functions ─────────────────────────────────────────
def score_title(candidate):
    title = candidate["profile"]["current_title"].lower()
    industry = candidate["profile"].get("current_industry", "").lower()

    for bad in BAD_TITLES:
        if bad in title:
            return 0.02

    for weak in WEAK_TITLES:
        if weak in title:
            return 0.15

    for strong in STRONG_AI_TITLES:
        if strong in title:
            score = 0.95
            if any(x in industry for x in ["technology", "software", "ai",
                                             "ml", "saas", "product", "fintech"]):
                score = min(score + 0.05, 1.0)
            if any(x in industry for x in ["it services", "consulting", "outsourcing"]):
                score = max(score - 0.15, 0.70)
            return round(score, 4)

    for acc in ACCEPTABLE_TITLES:
        if acc in title:
            score = 0.65
            if any(x in industry for x in ["technology", "software", "ai",
                                             "ml", "saas", "product", "fintech"]):
                score = min(score + 0.10, 0.80)
            if any(x in industry for x in ["it services", "consulting", "outsourcing"]):
                score = max(score - 0.15, 0.40)
            return round(score, 4)

    return 0.20


def score_skills(candidate):
    skills = candidate.get("skills", [])
    if not skills:
        return 0.0
    must_have = JD_PARSED["must_have_skills"]
    nice_to_have = JD_PARSED["nice_to_have_skills"]
    total_score = 0.0
    max_possible = 0.0
    for skill in skills:
        name = skill["name"].lower()
        prof = skill.get("proficiency", "beginner")
        endorsements = skill.get("endorsements", 0)
        duration = skill.get("duration_months", 0)
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
        prof_w = {"beginner": 0.2, "intermediate": 0.5,
                  "advanced": 0.8, "expert": 1.0}.get(prof, 0.3)
        endorse_w = min(endorsements / 20.0, 1.0)
        duration_w = min(duration / 24.0, 1.0)
        trust = 0.5 + 0.25 * endorse_w + 0.25 * duration_w
        total_score += relevance * prof_w * trust
        max_possible += relevance
    if max_possible == 0:
        return 0.0
    assessments = candidate["redrob_signals"].get("skill_assessment_scores", {})
    assessment_bonus = 0.0
    for skill_name, sc in assessments.items():
        for mh in must_have:
            if mh in skill_name.lower():
                assessment_bonus += sc / 100.0 * 0.05
                break
    return round(min(total_score / max_possible + assessment_bonus, 1.0), 4)


def score_career(candidate):
    history = candidate.get("career_history", [])
    if not history:
        return 0.1
    disq = JD_PARSED["disqualified_companies"]

    # ALSO check current title — if bad title, career score capped
    current_title = candidate["profile"]["current_title"].lower()
    title_is_bad = any(bad in current_title for bad in BAD_TITLES)
    title_is_weak = any(weak in current_title for weak in WEAK_TITLES)

    score = 0.5
    product_months = consulting_months = ai_months = total_months = 0

    for job in history:
        company = job.get("company", "").lower()
        title = job.get("title", "").lower()
        industry = job.get("industry", "").lower()
        duration = job.get("duration_months", 0)
        desc = job.get("description", "").lower()
        total_months += duration

        if any(d in company for d in disq) or \
           "it services" in industry or "consulting" in industry:
            consulting_months += duration
        else:
            product_months += duration

        ai_kw = ["embedding", "retrieval", "ranking", "recommendation",
                 "nlp", "ml", "machine learning", "search", "vector",
                 "model", "llm", "transformer", "rag", "fine-tun"]
        if any(kw in desc or kw in title for kw in ai_kw):
            ai_months += duration

        # Check if historical roles were AI-relevant titles
        for ai_role in AI_ROLE_TITLES:
            if ai_role in title:
                ai_months += duration * 0.3  # bonus for having good past titles
                break

    if total_months == 0:
        return 0.2

    consulting_ratio = consulting_months / total_months
    if consulting_ratio > 0.8:
        score -= 0.3
    elif consulting_ratio > 0.5:
        score -= 0.15

    score += (product_months / total_months) * 0.3
    ai_ratio = min(ai_months / total_months, 1.0)
    score += ai_ratio * 0.25

    # Cap career score if current title is bad/weak
    if title_is_bad:
        score = min(score, 0.30)  # Hard cap — bad title = career score capped
    elif title_is_weak:
        score = min(score, 0.55)  # Soft cap — weak title

    return round(max(0.0, min(1.0, score)), 4)


def score_experience(candidate):
    yoe = candidate["profile"].get("years_of_experience", 0)
    if 6 <= yoe <= 8:    return 1.0
    elif 5 <= yoe < 6:   return 0.75
    elif 8 < yoe <= 9:   return 0.80
    elif 9 < yoe <= 12:  return 0.55
    elif 4 <= yoe < 5:   return 0.60
    elif yoe < 4:        return 0.20
    else:                return 0.30


def _days_since(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days
    except:
        return 999


def score_behavioral(candidate):
    s = candidate.get("redrob_signals", {})
    score = 0.0
    if s.get("open_to_work_flag", False):
        score += 0.20
    days_inactive = _days_since(s.get("last_active_date", "2000-01-01"))
    if days_inactive <= 7:      score += 0.20
    elif days_inactive <= 30:   score += 0.15
    elif days_inactive <= 60:   score += 0.08
    elif days_inactive <= 180:  score += 0.02
    score += s.get("recruiter_response_rate", 0) * 0.15
    notice = s.get("notice_period_days", 90)
    if notice <= 30:    score += 0.15
    elif notice <= 60:  score += 0.08
    elif notice <= 90:  score += 0.04
    location = candidate["profile"].get("location", "").lower()
    country  = candidate["profile"].get("country", "").lower()
    preferred = ["pune", "noida", "delhi", "ncr", "hyderabad",
                 "mumbai", "bangalore", "bengaluru", "gurgaon"]
    if any(loc in location for loc in preferred):
        score += 0.12
    elif "india" in country and s.get("willing_to_relocate", False):
        score += 0.08
    elif s.get("willing_to_relocate", False):
        score += 0.04
    github = s.get("github_activity_score", -1)
    if github > 60:    score += 0.08
    elif github > 30:  score += 0.04
    score += (s.get("profile_completeness_score", 0) / 100.0) * 0.05
    if s.get("verified_email") and s.get("verified_phone"):
        score += 0.03
    score += s.get("interview_completion_rate", 0) * 0.02
    return round(min(score, 1.0), 4)


def generate_reasoning(ranked):
    c = ranked["_candidate"]
    p = c["profile"]
    s = c["redrob_signals"]
    bd = ranked["breakdown"]
    yoe = p.get("years_of_experience", 0)
    location = p.get("location", "Unknown")
    notice = s.get("notice_period_days", "?")
    days_inactive = _days_since(s.get("last_active_date", "2000-01-01"))
    response_rate = s.get("recruiter_response_rate", 0)
    open_to_work = s.get("open_to_work_flag", False)
    parts = [f"{p.get('current_title','Candidate')} with {yoe:.1f} yrs in {location}."]
    if bd["skills"] >= 0.65:
        parts.append("Strong endorsed AI/retrieval skills with platform assessments.")
    elif bd["skills"] >= 0.40:
        parts.append("Moderate skill match on core AI/ML skills.")
    else:
        parts.append("Limited match on core retrieval/ranking skills.")
    if bd["career"] >= 0.65:
        parts.append("Product-company career with AI-relevant work history.")
    elif bd["career"] < 0.35:
        parts.append("Career mostly in IT services — concern per JD criteria.")
    if days_inactive > 180:
        parts.append(f"Caution: last active {days_inactive} days ago.")
    elif not open_to_work:
        parts.append("Not marked open-to-work — outreach needed.")
    else:
        parts.append(f"Actively available; response rate {response_rate:.0%}.")
    if isinstance(notice, int) and notice <= 30:
        parts.append(f"Notice {notice}d — fits JD preference.")
    elif isinstance(notice, int) and notice > 90:
        parts.append(f"Notice {notice}d — longer than preferred.")
    return " ".join(parts)[:280]


def rank_candidates(candidates):
    results = []
    for c in candidates:
        t  = score_title(c)
        s  = score_skills(c)
        ca = score_career(c)
        e  = score_experience(c)
        b  = score_behavioral(c)
        final = (
            t  * WEIGHTS["title"] +
            s  * WEIGHTS["skills"] +
            ca * WEIGHTS["career"] +
            e  * WEIGHTS["experience"] +
            b  * WEIGHTS["behavioral"]
        )
        results.append({
            "candidate_id": c["candidate_id"],
            "score": round(final, 6),
            "breakdown": {"title": t, "skills": s, "career": ca,
                          "experience": e, "behavioral": b},
            "_candidate": c,
        })
    results.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    for i, r in enumerate(results[:100]):
        r["rank"] = i + 1
    return results


print("All functions loaded — v2 (strict title + career cap)!")