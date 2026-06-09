# Redrob Intelligent Candidate Ranking System

## Approach
A 5-component hybrid scoring system that ranks candidates
the way a great recruiter would — not by keyword matching,
but by understanding genuine fit.

## Architecture
Final Score =
  Title Fit Score      × 0.25
+ Skill Quality Score  × 0.25
+ Career Signal Score  × 0.20
+ Experience Fit       × 0.15
+ Behavioral Score     × 0.15

### Component 1 — Title Fit (25%)
Checks if current role is genuinely in AI/ML/Search space.
Penalizes IT services/consulting titles. This is the primary
honeypot and keyword-stuffer trap killer.

### Component 2 — Skill Quality (25%)
Not just "has skill" — scores based on endorsements +
duration_months + platform assessment scores. A skill listed
with 0 endorsements and 0 duration is treated as unreliable.

### Component 3 — Career Signal (20%)
Rewards product-company experience and AI-relevant work history
(embeddings, retrieval, ranking in job descriptions).
Penalizes careers spent entirely in IT outsourcing.

### Component 4 — Experience Fit (15%)
5–9 year band per JD. Ideal: 6–8 years (score=1.0).
Slightly outside band: partial credit. <4 years: near-zero.

### Component 5 — Behavioral Score (15%)
Uses all 23 Redrob platform signals:
- open_to_work_flag
- last_active_date (recency weighted)
- recruiter_response_rate
- notice_period_days (prefer ≤30)
- willing_to_relocate + location match
- github_activity_score
- profile_completeness_score
- verified_email + verified_phone

## Results
- Honeypots in top 100: 0/100 
- Candidates in 5–9yr band: 99/100 
- Open to work: 90/100 
- Score range: 0.9406 → 0.8700

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run ranker
python rank.py --candidates ./data/candidates.jsonl --out ./outputs/submission.csv

# Validate
python validate_submission.py outputs/submission.csv
```

## Compute
- Runtime: ~25 seconds on CPU
- RAM: <2 GB
- No GPU, no network calls during ranking
- Python 3.10

## AI Tools Used
Claude — architecture discussion and code review.
No candidate data was fed to any external LLM.