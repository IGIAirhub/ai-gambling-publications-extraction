#
#   Removed illegal streaming websites that were captured in our search (and is on OpenAlex?)
#
import json
import argparse
import os
import pandas as pd
import pyalex
from pyalex import Works

parser = argparse.ArgumentParser(description='Stage 4: re-query OpenAlex for every gambling-true id and build the corpus CSV.')
parser.add_argument("--input", default="master_gambling_classification.json", help="gambling classifier output {id: bool} (default: %(default)s)")
parser.add_argument("--output", default="filtered_openalex_works.csv", help="corpus CSV (default: %(default)s)")
args = parser.parse_args()

# OpenAlex asks API users for a contact email ("polite pool"). Set it before running:
#   export OPENALEX_EMAIL="you@example.org"
pyalex.config.email = os.environ.get("OPENALEX_EMAIL")
# A free OpenAlex API key is required for queries that page past the first page of
# results (stage 1). Create one at https://openalex.org/settings/api, then:
#   export OPENALEX_API_KEY="your-key"
pyalex.config.api_key = os.environ.get("OPENALEX_API_KEY")

# Helper function to reconstruct abstract from inverted index
def reconstruct_abstract(inv_idx):
    if not inv_idx:
        return None
    max_pos = max(pos for positions in inv_idx.values() for pos in positions)
    words = [None] * (max_pos + 1)
    for word, positions in inv_idx.items():
        for pos in positions:
            words[pos] = word
    return " ".join([w for w in words if w])

# Helper function to extract nested venue type
def get_venue_type(loc):
    """Safely reaches into the nested dictionary to find the venue type"""
    if loc and isinstance(loc, dict):
        source = loc.get('source')
        if source:
            return source.get('type', 'unknown')
    return 'unknown'

def extract_all_affiliations(authorships):
    """
    Extracts every unique institution and its country from all authors.
    """
    affiliations = []
    if not authorships:
        return affiliations

    for author in authorships:
        institutions = author.get('institutions', [])
        for inst in institutions:
            entry = {
                'name': inst.get('display_name'),
                'country': inst.get('country_code'),
                'sector': inst.get('type', 'unknown')
            }
            # Avoid duplicates if the same institution appears for multiple authors
            if entry not in affiliations:
                affiliations.append(entry)
                
    return affiliations
#
#   Add OpenAlex IDs to dataframe
#
with open(args.input, 'r') as f:
    raw_data = json.load(f)

true_ids = []

for work_id, is_true in raw_data.items():
    if is_true:
        true_ids.append(work_id)

df = pd.DataFrame(true_ids, columns=['openalex_id'])

print(df.head())
print(f"\nTotal works labeled TRUE: {len(df)}")


#
#   Fetch data from OpenAlex API
#
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

# 3. Create the Enrichment DataFrame
# We convert the list of API objects directly into a temporary table
df_api_results = pd.DataFrame(all_fetched_data)

# Apply abstract reconstruction
df_api_results['reconstructed_abstract'] = df_api_results['abstract_inverted_index'].apply(reconstruct_abstract)

df_api_results['title_abstract_combined'] = df_api_results.apply(
    lambda row: f"{row.get('display_name', '')}. {row.get('reconstructed_abstract', '')}".strip(), 
    axis=1
)

# Apply venue extraction onto primary location column
df_api_results['venue_type'] = df_api_results['primary_location'].apply(get_venue_type)

# Apply affiliation extraction onto authorships column
df_api_results['affiliations'] = df_api_results['authorships'].apply(extract_all_affiliations)


# 4. Clean up the API table (Keep only what we need)
# OpenAlex returns 'id' as the column name; we rename it to match our skeleton
df_api_results = df_api_results.rename(columns={'id': 'openalex_id'})

# Choose the specific columns you want to add to your dataset
# For example: ID, Publication Year, Title, and Citation Count
cols_to_keep = ['openalex_id', 'publication_year', 'display_name', 'title_abstract_combined', 'cited_by_count', 'venue_type', 'affiliations']
df_api_results = df_api_results[cols_to_keep]

# 5. The Relational Merge
# This "maps" the new data to the correct IDs in our skeleton
df_final = pd.merge(df, df_api_results, on='openalex_id', how='left')

# 6. Export
df_final.to_csv(args.output, index=False)