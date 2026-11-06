import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. Topic descriptions ---
topic_descriptions = {
    "Sports Betting": "AI methods model analyze historical data player statistics real-time variables predict event outcomes sports betting",
    "Online Problem Gambling": "AI methods player behavioral tracking data identify at-risk behavior digital gaming environments online problem gambling",
    "Gambling Decision Making": "AI methods neuroimaging behavioral data human brain processes rewards losses gambling decision making",
    "Gambling Website Detection": "automated web crawling classification algorithms identify categorize flag illicit unregulated gambling platforms internet",
    "Poker": "AI development poker game-theory algorithms reinforcement learning strategic decision-making imperfect information",
    "Casino Surveillance": "computer vision biometric technology fraud detection dealer errors blacklisted individuals casino surveillance"
}

# --- 2. Load CSV ---
df = pd.read_csv("ai_gambling_corpus.csv")

# --- 3. Clean up topic column (strip whitespace) ---
df["gambling_topic"] = df["gambling_topic"].str.strip()

# --- 4. Fit TF-IDF on all documents + topic descriptions together ---
all_texts = df["title_abstract_combined"].fillna("").tolist() + list(topic_descriptions.values())
vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform(all_texts)

doc_vectors = tfidf_matrix[:len(df)]
desc_vectors = tfidf_matrix[len(df):]

# --- 5. Find top 3 per topic ---
results = []

for i, (topic_name, _) in enumerate(topic_descriptions.items()):
    topic_mask = df["gambling_topic"] == topic_name
    topic_indices = df.index[topic_mask].tolist()

    if len(topic_indices) == 0:
        print(f"Warning: No documents found for topic '{topic_name}'")
        continue

    topic_doc_vectors = doc_vectors[topic_indices]
    similarities = cosine_similarity(desc_vectors[i], topic_doc_vectors).flatten()

    top_n = min(15, len(topic_indices))
    top_local_indices = similarities.argsort()[::-1][:top_n]
    top_global_indices = [topic_indices[j] for j in top_local_indices]

    top_df = df.loc[top_global_indices, [
        "openalex_id",
        "publication_year",
        "display_name",
        "title_abstract_combined",
        "cited_by_count",
        "venue_type",
        "affiliations",
        "gambling_topic",
        "ai_topics",
        "sport_topic"
    ]].copy()
    top_df["similarity_score"] = similarities[top_local_indices]
    top_df["rank"] = range(1, top_n + 1)
    results.append(top_df)

# --- 6. Save & preview ---
final_df = pd.concat(results, ignore_index=True)
final_df.to_csv("representative_publications.csv", index=False)

for topic, group in final_df.groupby("gambling_topic"):
    print(f"\n{'='*60}\n{topic}\n{'='*60}")
    for _, row in group.iterrows():
        print(f"  Rank {row['rank']} [{row['similarity_score']:.3f}] {row['display_name']}")
        if row['sport_topic'] != "Not Applicable":
            print(f"    Sport: {row['sport_topic']}")