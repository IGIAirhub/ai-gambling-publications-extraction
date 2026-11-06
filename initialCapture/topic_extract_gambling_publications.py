#
#
#    This script extracts publications related to gambling from the OpenAlex database.
#    It searches for works containing the term "gambling" in their title or abstract,
#    published between 2010 and 2025, and saves the results in a JSON file.
#
#


from itertools import chain
import pyalex
from pyalex import Works
import json
import argparse
import os

parser = argparse.ArgumentParser(description='Stage 1: OpenAlex topic-ID query.')
parser.add_argument("--output", default="topictest.json", help="output JSON (default: %(default)s)")
args = parser.parse_args()

OUTPUT_FILE = args.output
# OpenAlex asks API users for a contact email ("polite pool"). Set it before running:
#   export OPENALEX_EMAIL="you@example.org"
pyalex.config.email = os.environ.get("OPENALEX_EMAIL")
# A free OpenAlex API key is required for queries that page past the first page of
# results (stage 1). Create one at https://openalex.org/settings/api, then:
#   export OPENALEX_API_KEY="your-key"
pyalex.config.api_key = os.environ.get("OPENALEX_API_KEY")

def reconstruct_abstract(inv_idx):
    if not inv_idx:
        return None
    max_pos = max(pos for positions in inv_idx.values() for pos in positions)
    words = [None] * (max_pos + 1)
    for word, positions in inv_idx.items():
        for pos in positions:
            words[pos] = word
    return " ".join([w for w in words if w])

# T11674 = Sports Analytics and Performance
# T11705 = Gambling Behavior and Treatments

pager = (
    Works()
    .filter(**{
                "primary_topic.id": "T11674|T11705",
                "from_publication_date": "2010-01-01",
                "to_publication_date": "2025-12-31",
                "type": "article|review|book-chapter|book",
                "language": "en"
              }
           )
    .paginate(per_page=200, n_max=None)
)

# Dictionary of publications
publications = {}

for work in chain.from_iterable(pager):
    work_id = work.get("id", "unknown_id")
    title = work.get("display_name", "No Title")
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    keywords_list = [c["display_name"] for c in work.get("concepts", [])]
    keywords = ", ".join(keywords_list) if keywords_list else "No Keywords"

    publications[work_id] = {
        "title": title,
        "abstract": abstract,
        # "abstract": "",
        # "keywords": keywords
        "keywords": ""
    }

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(publications, f, indent=2, ensure_ascii=False)
