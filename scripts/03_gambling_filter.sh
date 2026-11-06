#!/usr/bin/env bash
# Stage 3 - The same gambling classifier, run twice on different inputs.
#   a) AI-true papers   -> master_gambling_classification.json   (the AI + gambling corpus)
#   b) the full dataset -> gambling_classifier_on_master.json    (all gambling papers; the
#      denominator for the "% of gambling research that is AI" figure)
#      -> just_gambling_publications.csv
#
# Skip (b) with SKIP_DENOMINATOR=1. It classifies every paper in the dataset (~100k LLM calls).
source "$(dirname "$0")/common.sh"
require_ollama deepseek-r1:14b
require_file attempt_2_postAIClassifcation.json

run classifiers/binaryGamblingClassification.py \
    --input attempt_2_postAIClassifcation.json --output master_gambling_classification.json

if [[ "${SKIP_DENOMINATOR:-0}" == "1" ]]; then
    log "SKIP_DENOMINATOR=1: skipping the full-dataset run (percentAIInGambling.py will not work)"
    exit 0
fi

require_openalex
require_file master_gambling_dataset.json
run classifiers/binaryGamblingClassification.py \
    --input master_gambling_dataset.json --output gambling_classifier_on_master.json
run corpusBuilding/extractGamblingPaperYears.py \
    --input gambling_classifier_on_master.json --output just_gambling_publications.csv
