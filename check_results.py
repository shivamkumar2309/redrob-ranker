import csv

with open('outputs/submission.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print('TOP 10 RANKED CANDIDATES:')
print(f"{'Rank':<5} {'ID':<14} {'Score':<8} Reasoning")
print('-'*90)
for r in rows[:10]:
    print(f"{r['rank']:<5} {r['candidate_id']:<14} {r['score']:<8} {r['reasoning'][:70]}")

print()
print('BOTTOM 5 of top 100:')
for r in rows[95:]:
    print(f"{r['rank']:<5} {r['candidate_id']:<14} {r['score']:<8} {r['reasoning'][:70]}")

print()
# Score distribution
scores = [float(r['score']) for r in rows]
print(f"Score range: {scores[0]:.4f} (rank 1) → {scores[-1]:.4f} (rank 100)")
print(f"Score at rank 10:  {scores[9]:.4f}")
print(f"Score at rank 50:  {scores[49]:.4f}")