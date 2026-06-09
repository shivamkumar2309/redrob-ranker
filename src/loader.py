import gzip
import json
from tqdm import tqdm

def load_candidates(path: str) -> list[dict]:
    """Load candidates from JSONL or gzipped JSONL (.jsonl.gz)"""
    candidates = []
    print(f"Loading candidates from {path}...")

    if path.endswith(".gz"):
        opener = lambda: gzip.open(path, "rt", encoding="utf-8")
    else:
        opener = lambda: open(path, "r", encoding="utf-8")

    with opener() as f:
        for line in tqdm(f, desc="Reading"):
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    print(f" Loaded {len(candidates):,} candidates.")
    return candidates