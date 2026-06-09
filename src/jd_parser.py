# hardcoded parsed structure for JD

JD_PARSED = {
    "title": "Senior AI Engineer",
    "experience_min": 5,
    "experience_max": 9,
    "experience_ideal_min": 6,
    "experience_ideal_max": 8,

    # MUST HAVE skills (production experience required)
    "must_have_skills": [
        "embeddings", "sentence-transformers", "vector database",
        "faiss", "pinecone", "weaviate", "qdrant", "milvus",
        "elasticsearch", "opensearch", "semantic search",
        "retrieval", "ranking", "recommendation", "RAG",
        "NDCG", "MRR", "MAP", "evaluation", "A/B testing",
        "python", "NLP", "information retrieval",
        "hybrid search", "dense retrieval", "BM25",
    ],

    # NICE TO HAVE
    "nice_to_have_skills": [
        "fine-tuning", "LoRA", "QLoRA", "PEFT",
        "learning-to-rank", "XGBoost", "LLM",
        "distributed systems", "open-source",
    ],

    # Preferred locations
    "preferred_locations": [
        "pune", "noida", "delhi", "ncr", "hyderabad",
        "mumbai", "bangalore", "bengaluru", "gurgaon",
        "india"
    ],

    # Disqualified company types (explicit in JD)
    "disqualified_companies": [
        "tcs", "infosys", "wipro", "accenture",
        "cognizant", "capgemini", "mindtree", "mphasis",
        "hexaware", "tech mahindra"
    ],

    # Disqualified if ENTIRE career is in these
    "disqualified_domains": [
        "computer vision", "speech recognition",
        "robotics", "marketing", "sales", "hr", "operations"
    ],

    # Notice period preference
    "preferred_notice_max_days": 30,
    "acceptable_notice_max_days": 90,

    # Work mode
    "preferred_work_modes": ["hybrid", "flexible", "onsite"],
}