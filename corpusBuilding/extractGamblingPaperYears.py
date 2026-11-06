import json
import argparse
import os
import pandas as pd
import pyalex
from pyalex import Works

parser = argparse.ArgumentParser(description='Denominator: publication years for every gambling-true paper in the full dataset.')
parser.add_argument("--input", default="gambling_classifier_on_master.json", help="gambling classifier output on the full dataset {id: bool} (default: %(default)s)")
parser.add_argument("--output", default="just_gambling_publications.csv", help="CSV of openalex_id, publication_year (default: %(default)s)")
args = parser.parse_args()

# OpenAlex asks API users for a contact email ("polite pool"). Set it before running:
#   export OPENALEX_EMAIL="you@example.org"
pyalex.config.email = os.environ.get("OPENALEX_EMAIL")
# A free OpenAlex API key is required for queries that page past the first page of
# results (stage 1). Create one at https://openalex.org/settings/api, then:
#   export OPENALEX_API_KEY="your-key"
pyalex.config.api_key = os.environ.get("OPENALEX_API_KEY")

with open(args.input, 'r') as f:
    raw_data = json.load(f)

true_ids = []

for work_id, is_true in raw_data.items():
    if is_true:
        true_ids.append(work_id)

df = pd.DataFrame(true_ids, columns=['openalex_id'])

print(df.head())
print(f"\nTotal works labeled TRUE: {len(df)}")

batch_size = 25  # Best practice: Fetch in chunks to avoid URL length limits
all_fetched_data = []

print(f"Starting enrichment for {len(true_ids)} works...")

for i in range(0, len(true_ids), batch_size):
    # Slice our list into a chunk of 25
    chunk = true_ids[i : i + batch_size]
    
    # Create the filter string (ID1|ID2|ID3...)
    query_filter = "|".join(chunk)
    
    # One API call for 25 works
    results = Works().filter(openalex=query_filter).get()
    all_fetched_data.extend(results)
    print(f"Fetched {len(all_fetched_data)} / {len(true_ids)}...")

df_api_results = pd.DataFrame(all_fetched_data)
df_api_results = df_api_results.rename(columns={'id': 'openalex_id'})

cols_to_keep = ['openalex_id', 'publication_year']
df_api_results = df_api_results[cols_to_keep]

df_final = pd.merge(df, df_api_results, on='openalex_id', how='left')

df_final.to_csv(args.output, index=False)