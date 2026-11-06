import json
import argparse

parser = argparse.ArgumentParser(description='Stage 1: merge the topic and term query results.')
parser.add_argument("--topics", default="query_by_topics.json", help="topic-query JSON (default: %(default)s)")
parser.add_argument("--terms", default="query_by_terms.json", help="term-query JSON (default: %(default)s)")
parser.add_argument("--output", default="master_gambling_dataset.json", help="merged output JSON (default: %(default)s)")
args = parser.parse_args()

# Load the two results
with open(args.topics, "r") as f:
    topics_data = json.load(f)

with open(args.terms, "r") as f:
    terms_data = json.load(f)

# Merge dictionaries: 
# This creates a new dictionary containing everything from both.
# If a Key (ID) exists in both, the 'terms_data' version will be kept.
master_publications = {**topics_data, **terms_data}

print(f"Topics found: {len(topics_data)}")
print(f"Terms found: {len(terms_data)}")
print(f"Unique total: {len(master_publications)}")

# Save the master dictionary
with open(args.output, "w", encoding="utf-8") as f:
    json.dump(master_publications, f, indent=2, ensure_ascii=False)