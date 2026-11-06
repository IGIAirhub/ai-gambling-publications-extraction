"""
Top 10 organizations by number of publications (2020–2025)

Filters the corpus for recent research (2020–2025) and identifies the top 
performing institutions by publication count. Employs a robust de-duplication 
strategy to ensure each paper is credited once per unique organization.
"""

import pandas as pd
import matplotlib.pyplot as plt
import ast

# 1) Load data
df = pd.read_csv("ai_gambling_corpus.csv")

# --- NEW FILTERING STEP ---
# Filter for years 2020 through 2025
df = df[(df["publication_year"] >= 2020) & (df["publication_year"] <= 2025)]
# ---------------------------

# 2) Parse affiliations (string -> list[dict])
def parse_affiliations(x):
    try:
        return ast.literal_eval(x) if isinstance(x, str) else (x if isinstance(x, list) else [])
    except Exception:
        return []

df["affiliations"] = df["affiliations"].apply(parse_affiliations)

# 3) Explode to (paper, org) pairs with de-dup per paper
paper_id_col = None
for candidate in ["id", "work_id", "openalex_id", "doi"]:
    if candidate in df.columns:
        paper_id_col = candidate
        break

if paper_id_col is None:
    df = df.reset_index().rename(columns={"index": "paper_id"})
    paper_id_col = "paper_id"

org_rows = []
for _, row in df.iterrows():
    paper_id = row[paper_id_col]
    seen = set()
    for aff in row["affiliations"]:
        if isinstance(aff, dict):
            org = aff.get("name")
            if org and org not in seen:
                org_rows.append({"paper_id": paper_id, "org": org})
                seen.add(org)

df_orgs = pd.DataFrame(org_rows)

# 4) Count publications per organization
org_counts = (
    df_orgs.groupby("org")["paper_id"]
    .nunique()
    .sort_values(ascending=False)
)

top10 = org_counts.head(10)

# 5) Plot
plt.figure(figsize=(12, 7))
bars = plt.bar(top10.index, top10.values)

# Updated title for 2020-2025
plt.title("Top 10 organizations by number of publications (2020–2025)", loc="left", fontweight="bold")
plt.ylabel("Number of publications")
plt.xticks(rotation=45, ha="right")

# value labels
plt.bar_label(bars, padding=3)

# clean style
ax = plt.gca()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="y", alpha=0.2)

plt.tight_layout()

# Updated filename for 2020-2025
plt.savefig("top10_orgs_publications_2020_2025.png", dpi=300)
plt.show()