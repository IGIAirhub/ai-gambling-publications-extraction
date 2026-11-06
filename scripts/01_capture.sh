#!/usr/bin/env bash
# Stage 1 - Query OpenAlex two ways and merge.
#   out: query_by_terms.json, query_by_topics.json, master_gambling_dataset.json
source "$(dirname "$0")/common.sh"
require_openalex strict

run initialCapture/terms_extract_gambling_publications.py --output query_by_terms.json
run initialCapture/topic_extract_gambling_publications.py --output query_by_topics.json
run initialCapture/dataset_merger.py \
    --topics query_by_topics.json --terms query_by_terms.json --output master_gambling_dataset.json
