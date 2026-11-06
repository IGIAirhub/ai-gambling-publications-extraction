#!/usr/bin/env bash
# Stage 4 - Re-query OpenAlex for every AI + gambling paper and build the corpus table.
#   in:  master_gambling_classification.json
#   out: filtered_openalex_works.csv   <-- THE CORPUS, after the manual review below
source "$(dirname "$0")/common.sh"
require_openalex
require_file master_gambling_classification.json

run corpusBuilding/dataAnalysis.py \
    --input master_gambling_classification.json --output filtered_openalex_works.csv

cat <<EOF

------------------------------------------------------------------------------
MANUAL REVIEW STEP
Open $DATA_DIR/filtered_openalex_works.csv and delete any rows that are not
research publications. In the published run, 9 rows were pirated sports
live-stream pages indexed by OpenAlex (titles like "Dolphins vs Steelers Live
Free Online TV Broadcast"). They were removed by hand: 908 -> 899 papers.
Save the file under the same name before running stage 5.
------------------------------------------------------------------------------
EOF
