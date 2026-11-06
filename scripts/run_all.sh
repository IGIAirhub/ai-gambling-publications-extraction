#!/usr/bin/env bash
# Run the pipeline stages in order.
#
#   ./scripts/run_all.sh                 stages 1-6
#   ./scripts/run_all.sh --from 4        resume at stage 4
#   ./scripts/run_all.sh --from 2 --to 3
#
# Stage 4 ends with a manual review of the corpus. When run from a terminal, this
# script pauses there until you press Enter. Topic discovery is separate:
# scripts/topic_discovery.sh.
set -euo pipefail
cd "$(dirname "$0")"

from=1; to=6
while (( $# )); do
    case "$1" in
        --from) from="$2"; shift 2 ;;
        --to)   to="$2";   shift 2 ;;
        -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
        *) echo "unknown option: $1" >&2; exit 1 ;;
    esac
done

stages=(01_capture 02_ai_filter 03_gambling_filter 04_build_corpus 05_topic_classification 06_visualize)
for i in "${!stages[@]}"; do
    n=$((i + 1))
    (( n < from || n > to )) && continue
    printf '\n\033[1;34m######## Stage %d: %s ########\033[0m\n' "$n" "${stages[$i]}"
    "./${stages[$i]}.sh"
    if (( n == 4 && to > 4 )) && [[ -t 0 ]]; then
        read -r -p "Review the corpus as described above, then press Enter to continue to stage 5... "
    fi
done
