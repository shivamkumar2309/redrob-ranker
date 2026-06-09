from src.scorer import score_title, score_skills, score_career, score_experience
from src.behavioral import score_behavioral
from tqdm import tqdm

# Weights 
WEIGHTS = {
    "title":      0.25,
    "skills":     0.25,
    "career":     0.20,
    "experience": 0.15,
    "behavioral": 0.15,
}

def rank_candidates(candidates: list[dict]) -> list[dict]:
    results = []

    for c in tqdm(candidates, desc="Scoring"):
        t_score = score_title(c)
        s_score = score_skills(c)
        ca_score = score_career(c)
        e_score = score_experience(c)
        b_score = score_behavioral(c)

        final = (
            t_score  * WEIGHTS["title"] +
            s_score  * WEIGHTS["skills"] +
            ca_score * WEIGHTS["career"] +
            e_score  * WEIGHTS["experience"] +
            b_score  * WEIGHTS["behavioral"]
        )

        results.append({
            "candidate_id": c["candidate_id"],
            "score": round(final, 6),
            "breakdown": {
                "title": t_score,
                "skills": s_score,
                "career": ca_score,
                "experience": e_score,
                "behavioral": b_score,
            },
            "_candidate": c,  # keep reference for reasoning
        })

    # Sort by score descending, tie-break by candidate_id ascending
    results.sort(key=lambda x: (-x["score"], x["candidate_id"]))

    # Assign ranks 1-100 for top 100
    for i, r in enumerate(results[:100]):
        r["rank"] = i + 1

    return results