#!/usr/bin/env bash
# Stage 2 - Keep AI-related papers, then re-attach their title + abstract.
#   in:  master_gambling_dataset.json
#   out: master_ai_classification.json   {id: true/false}
#        attempt_2_postAIClassifcation.json   {id: {title, abstract}} for every AI-true id
#        missing_entries.json   AI-true ids whose OpenAlex fetch failed (only written if any)
source "$(dirname "$0")/common.sh"
require_openalex
require_ollama deepseek-r1:14b
require_file master_gambling_dataset.json

# Slow: one LLM call per paper. Safe to stop and re-run; it resumes from its output file.
run classifiers/binaryAIClassification.py \
    --input master_gambling_dataset.json --output master_ai_classification.json

run classifiers/postAIClassifcation.py \
    --input master_ai_classification.json --output attempt_2_postAIClassifcation.json

# Integrity check: every AI-true paper should now have a title/abstract record.
run classifiers/missingEntries.py \
    --master master_ai_classification.json --results attempt_2_postAIClassifcation.json \
    --output missing_entries.json
