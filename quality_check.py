"""
Quality Check Script — Redrob Hackathon
Checks:
1. Honeypot detection in top 100
2. Score distribution analysis
3. Diversity of titles/locations
4. Flag any suspicious candidates
"""

import csv
import json
import gzip
from datetime import date, datetime

# ── Load submission ──────────────────────────────────────────
with open('outputs/submission.csv', encoding='utf-8') as f:
    submission = {r['candidate_id']: r for r in csv.DictReader(f)}

top100_ids = set(submission.keys())

# ── Load candidates (only top 100 for speed) ─────────────────
print("Loading candidates (scanning for top 100)...")
top100_candidates = {}

try:
    with open('data/candidates.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            c = json.loads(line)
            if c['candidate_id'] in top100_ids:
                top100_candidates[c['candidate_id']] = c
            if len(top100_candidates) == 100:
                break
except:
    with gzip.open('data/candidates.jsonl.gz', 'rt', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            c = json.loads(line)
            if c['candidate_id'] in top100_ids:
                top100_candidates[c['candidate_id']] = c
            if len(top100_candidates) == 100:
                break

print(f"Found {len(top100_candidates)} of top 100 candidates\n")

# ── HONEYPOT CHECK ────────────────────────────────────────────
print("=" * 60)
print("HONEYPOT CHECK")
print("=" * 60)

honeypot_flags = []
today = date.today()

for cid, c in top100_candidates.items():
    p = c['profile']
    history = c.get('career_history', [])
    s = c['redrob_signals']
    flags = []

    # 1. Experience vs career dates mismatch
    yoe = p.get('years_of_experience', 0)
    if history:
        try:
            earliest = min(
                datetime.strptime(j['start_date'], "%Y-%m-%d").date()
                for j in history if j.get('start_date')
            )
            actual_yoe = (today - earliest).days / 365.25
            if abs(actual_yoe - yoe) > 3:
                flags.append(f"YoE mismatch: profile says {yoe:.1f}y but history shows {actual_yoe:.1f}y")
        except:
            pass

    # 2. Company founded after start date (impossible tenure)
    for job in history:
        duration = job.get('duration_months', 0)
        if duration > 600:  # 50 years at one company — impossible
            flags.append(f"Impossible tenure: {duration} months at {job.get('company')}")

    # 3. Total career months vs claimed experience
    total_months = sum(j.get('duration_months', 0) for j in history)
    if total_months > 0 and yoe > 0:
        history_years = total_months / 12
        if history_years > yoe * 2:  # History claims 2x more than profile
            flags.append(f"Duration inflation: {history_years:.1f}y history vs {yoe}y claimed")

    # 4. Skills with 0 endorsements AND 0 duration (keyword stuffer signal)
    skills = c.get('skills', [])
    ghost_skills = [sk['name'] for sk in skills
                    if sk.get('endorsements', 0) == 0
                    and sk.get('duration_months', 0) == 0]
    if len(ghost_skills) > 8:
        flags.append(f"Keyword stuffer? {len(ghost_skills)} skills with 0 endorsements+duration: {ghost_skills[:5]}")

    # 5. Profile completeness vs reality
    completeness = s.get('profile_completeness_score', 100)
    if completeness < 20:
        flags.append(f"Very low profile completeness: {completeness}%")

    # 6. Impossible signal values
    github = s.get('github_activity_score', 0)
    response_rate = s.get('recruiter_response_rate', 0)
    if github > 100 or response_rate > 1:
        flags.append(f"Impossible signal values: github={github}, response_rate={response_rate}")

    if flags:
        rank = submission[cid]['rank']
        score = submission[cid]['score']
        honeypot_flags.append((int(rank), cid, flags))
        print(f"Rank {rank} | {cid} | Score {score}")
        for flag in flags:
            print(f"       → {flag}")

if not honeypot_flags:
    print("  No honeypot signals detected in top 100!")
else:
    print(f"\n  Total flagged: {len(honeypot_flags)}/100")
    print(f"  Disqualification threshold: >10 honeypots in top 100")
    if len(honeypot_flags) <= 5:
        print(f"  Well within safe zone ({len(honeypot_flags)}/10 limit)")
    elif len(honeypot_flags) <= 10:
        print(f"  Getting close to limit — consider reviewing these")
    else:
        print(f"  DANGER: Over the 10 honeypot limit!")

# ── TITLE DIVERSITY ───────────────────────────────────────────
print("\n" + "=" * 60)
print("TITLE DISTRIBUTION in Top 100")
print("=" * 60)
from collections import Counter

titles = []
locations = []
yoe_list = []
open_to_work = 0
notice_under30 = 0

for cid, c in top100_candidates.items():
    p = c['profile']
    s = c['redrob_signals']
    titles.append(p.get('current_title', 'Unknown'))
    locations.append(p.get('location', 'Unknown').split(',')[0].strip())
    yoe_list.append(p.get('years_of_experience', 0))
    if s.get('open_to_work_flag'):
        open_to_work += 1
    if s.get('notice_period_days', 999) <= 30:
        notice_under30 += 1

title_counts = Counter(titles).most_common(10)
for title, count in title_counts:
    bar = '█' * count
    print(f"  {title:<40} {bar} ({count})")

print(f"\nTop Locations:")
loc_counts = Counter(locations).most_common(8)
for loc, count in loc_counts:
    print(f"  {loc:<30} {count}")

print(f"\nExperience Stats:")
print(f"  Average YoE:     {sum(yoe_list)/len(yoe_list):.1f} years")
print(f"  Min YoE:         {min(yoe_list):.1f} years")
print(f"  Max YoE:         {max(yoe_list):.1f} years")
print(f"  In 5-9yr band:   {sum(1 for y in yoe_list if 5 <= y <= 9)}/100")

print(f"\nAvailability Signals:")
print(f"  Open to work:    {open_to_work}/100")
print(f"  Notice ≤30 days: {notice_under30}/100")

# ── SCORE DISTRIBUTION ────────────────────────────────────────
print("\n" + "=" * 60)
print("SCORE DISTRIBUTION")
print("=" * 60)
scores = [float(r['score']) for r in submission.values()]
scores.sort(reverse=True)

bands = [(1,10), (11,25), (26,50), (51,75), (76,100)]
for lo, hi in bands:
    band_scores = scores[lo-1:hi]
    avg = sum(band_scores)/len(band_scores)
    print(f"  Rank {lo:>3}-{hi:<3}: avg score {avg:.4f}  (min {min(band_scores):.4f} / max {max(band_scores):.4f})")

print("\nQuality check complete!")
print("\nSUMMARY:")
print(f"  Honeypots in top 100: {len(honeypot_flags)} (limit: 10)")
print(f"  Candidates in 5-9yr band: {sum(1 for y in yoe_list if 5 <= y <= 9)}/100")
print(f"  Open to work: {open_to_work}/100")
print(f"  Score range: {scores[0]:.4f} → {scores[99]:.4f}")