#!/usr/bin/env bash
# Stage 6 - Every figure and summary table.
#   in:  ai_gambling_corpus.csv, filtered_openalex_works.csv,
#        gambling_topic_classified_papers.csv, just_gambling_publications.csv (stage 3b)
#   out: figures/*.png, plus representative_publications.csv and ai_gambling_with_regions.csv
source "$(dirname "$0")/common.sh"
require_file ai_gambling_corpus.csv filtered_openalex_works.csv gambling_topic_classified_papers.csv

failed=()
for script in "$REPO_DIR"/visualizations/*.py; do
    name="visualizations/$(basename "$script")"
    if [[ "$name" == visualizations/percentAIInGambling.py && ! -s just_gambling_publications.csv ]]; then
        log "skipping $name (needs just_gambling_publications.csv from stage 3b)"
        continue
    fi
    run "$name" || failed+=("$name")
done

mkdir -p figures
shopt -s nullglob
pngs=(*.png)
(( ${#pngs[@]} )) && mv -f "${pngs[@]}" figures/
log "figures written to $DATA_DIR/figures"

if (( ${#failed[@]} )); then
    die "these scripts failed: ${failed[*]}"
fi
