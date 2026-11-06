# LEGACY: not part of the pipeline. Its output is not read by any other script.
# Kept for the record only.
import json
import os
import pyalex
from pyalex import Works

# Configuration
# OpenAlex asks API users for a contact email ("polite pool"). Set it before running:
#   export OPENALEX_EMAIL="you@example.org"
pyalex.config.email = os.environ.get("OPENALEX_EMAIL")
INPUT_FILE = 'gambling_results_from_2010-01-01_deepseek-r1-14b.json'
OUTPUT_FILE = 'postAIClassifcation.json'

def reconstruct_abstract(inv_idx):
    if not inv_idx:
        return None
    max_pos = max(pos for positions in inv_idx.values() for pos in positions)
    words = [None] * (max_pos + 1)
    for word, positions in inv_idx.items():
        for pos in positions:
            words[pos] = word
    return " ".join([w for w in words if w])

# 1. Load the input JSON
with open(INPUT_FILE, 'r') as f:
    input_data = json.load(f)

final_results = {}

# 2. Iterate and fetch if True
for link, should_extract in input_data.items():
    if should_extract:
        print(f"Fetching: {link}")
        try:
            # Fetch specific work record
            work = Works()[link]
            
            final_results[link] = {
                "title": work.get("display_name", "No Title"),
                "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
                "keywords": ""
            }
        except Exception as e:
            print(f"Failed to fetch {link}: {e}")

# 3. Save to new JSON file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(final_results, f, indent=2, ensure_ascii=False)

print(f"Done! Saved {len(final_results)} records to {OUTPUT_FILE}")