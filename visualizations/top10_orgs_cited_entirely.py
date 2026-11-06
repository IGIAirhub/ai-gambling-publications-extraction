"""
Top 10 organizations by output in the Top 100 most-cited publications, 2010–25

Identifies the "Citation Elite" by filtering the corpus for the 100 most 
frequently cited works and ranking the organizations associated with them. 
This provides a measure of institutional influence and research impact 
rather than simple publication volume.
"""

import pandas as pd
import matplotlib.pyplot as plt
import ast

# --- CONFIGURATION ---
INPUT_FILE = "ai_gambling_corpus.csv"
TOP_N_CITED_PAPERS = 100
TOP_N_ORGS = 10

# 1) Load data
df = pd.read_csv(INPUT_FILE)

# 2) Parse affiliations (string -> list[dict])
def parse_affiliations(x):
    try:
        return ast.literal_eval(x) if isinstance(x, str) else (x if isinstance(x, list) else [])
    except Exception:
        return []

df["affiliations"] = df["affiliations"].apply(parse_affiliations)

# 3) Choose stable paper id column if present; otherwise fall back to row index
paper_id_col = None
for candidate in ["id", "work_id", "openalex_id", "doi"]:
    if candidate in df.columns:
        paper_id_col = candidate
        break

if paper_id_col is None:
    df = df.reset_index().rename(columns={"index": "paper_id"})
    paper_id_col = "paper_id"

# 4) Identify the citation count column (common OpenAlex exports)
cited_by_col = None
for candidate in ["cited_by_count", "cited_by", "citations", "citation_count", "times_cited"]:
    if candidate in df.columns:
        cited_by_col = candidate
        break

if cited_by_col is None:
    raise ValueError(
        "Could not find a citation count column. Expected one of: "
        "cited_by_count, cited_by, citations, citation_count, times_cited"
    )

# Ensure citations are numeric
df[cited_by_col] = pd.to_numeric(df[cited_by_col], errors="coerce").fillna(0)

# 5) Filter to Top 100 most cited publications
df_top = df.sort_values(by=cited_by_col, ascending=False).head(TOP_N_CITED_PAPERS).copy()

# 6) Explode to (paper, org) pairs with de-dup per paper (same as your logic)
org_rows = []
for _, row in df_top.iterrows():
    paper_id = row[paper_id_col]
    seen = set()
    for aff in row["affiliations"]:
        if isinstance(aff, dict):
            org = aff.get("name")
            if org and org not in seen:
                org_rows.append({"paper_id": paper_id, "org": org})
                seen.add(org)

df_orgs = pd.DataFrame(org_rows)

# 7) Count publications per organization (each paper counts once per org)
org_counts = (
    df_orgs.groupby("org")["paper_id"]
    .nunique()
    .sort_values(ascending=False)
)

top10 = org_counts.head(TOP_N_ORGS)

# 8) Plot (keep styling consistent)
plt.figure(figsize=(12, 7))
bars = plt.bar(top10.index, top10.values)

plt.title(
    f"Top {TOP_N_ORGS} organizations by number of publications in the Top {TOP_N_CITED_PAPERS} most cited (2010-2025)",
    loc="left",
    fontweight="bold",
)
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
plt.savefig(f"top{TOP_N_ORGS}_orgs_in_top{TOP_N_CITED_PAPERS}_most_cited.png", dpi=300)
plt.show()
