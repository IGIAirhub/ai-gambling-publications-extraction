import json
import argparse
import os
import pyalex
from pyalex import Works

# Configuration
parser = argparse.ArgumentParser(description='Stage 2: fetch title + abstract from OpenAlex for every id marked true.')
parser.add_argument("--input", default="recovered_entries.json", help="input JSON {id: bool} (default: %(default)s)")
parser.add_argument("--output", default="POST_recovered_entries.json", help="output JSON {id: {title, abstract}} (default: %(default)s)")
args = parser.parse_args()

# OpenAlex asks API users for a contact email ("polite pool"). Set it before running:
#   export OPENALEX_EMAIL="you@example.org"
pyalex.config.email = os.environ.get("OPENALEX_EMAIL")
# A free OpenAlex API key is required for queries that page past the first page of
# results (stage 1). Create one at https://openalex.org/settings/api, then:
#   export OPENALEX_API_KEY="your-key"
pyalex.config.api_key = os.environ.get("OPENALEX_API_KEY")
INPUT_FILE = args.input
OUTPUT_FILE = args.output

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