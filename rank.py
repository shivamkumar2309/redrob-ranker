#!/usr/bin/env python3
"""
Redrob Hackathon — Candidate Ranking System
Usage: python rank.py --candidates D:/redrob-ranker/data/candidates.jsonl --out D:/redrob-ranker/outputs/submission.csv
"""

import argparse
import csv
import os
from src.loader import load_candidates
from src.ranker import rank_candidates
from src.reasoning import generate_reasoning

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="D:/redrob-ranker/data/candidates.jsonl",
                        help="Path to candidates.jsonl or candidates.jsonl")
    parser.add_argument("--out", default="D:/redrob-ranker/outputs/submission.csv",
                        help="Output CSV path")
    parser.add_argument("--top", type=int, default=100,
                        help="Number of candidates to output (default 100)")
    args = parser.parse_args()

    # Step 1: Load
    candidates = load_candidates(args.candidates)

    # Step 2: Rank
    ranked = rank_candidates(candidates)
    top100 = ranked[:args.top]

    # Step 3: Generate reasoning
    print("Generating reasoning strings...")
    for r in top100:
        r["reasoning"] = generate_reasoning(r)

    # Step 4: Write CSV
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for r in top100:
            writer.writerow([
                r["candidate_id"],
                r["rank"],
                r["score"],
                r["reasoning"],
            ])

    print(f"\n Done! Submission saved to: {args.out}")
    print(f"   Total candidates scored: {len(ranked):,}")
    print(f"   Top candidate score: {top100[0]['score']:.4f}")
    print(f"   Rank 100 score: {top100[-1]['score']:.4f}")

if __name__ == "__main__":
    main()