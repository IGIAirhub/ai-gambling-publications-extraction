#!/usr/bin/env bash
# OPTIONAL, exploratory - BERTopic topic discovery. Not part of run_all.sh.
#
# This is how the topic label lists used in stage 5 were found. Nothing downstream
# reads its output: the final labels are written into the stage 5 classifier prompts.
# It is iterative and needs human judgement - see "Topic discovery" in README.md.
#
#   ./scripts/topic_discovery.sh first           cluster the whole corpus
#   ./scripts/topic_discovery.sh refine <N>      drop resolved topics from the previous
#                                                run and re-cluster the rest (run N = 2, 3, ...)
source "$(dirname "$0")/common.sh"
require_ollama qwen3:14b

case "${1:-}" in
    first)
        require_file filtered_openalex_works.csv
        run topicDiscovery/topicExtract.py \
            --input filtered_openalex_works.csv --text-column title_abstract_combined \
            --topics-output discovered_gambling_topics_run1.csv \
            --docs-output paper_to_gambling_topic_run1.csv
        ;;
    refine)
        n="${2:?usage: topic_discovery.sh refine <run number, e.g. 2>}"
        prev=$((n - 1))
        require_file "paper_to_gambling_topic_run${prev}.csv"
        echo "Edit the topic numbers in topicDiscovery/filter_sportsbetting_poker.py to the ones"
        echo "you want to DROP from run ${prev}, then press Enter (Ctrl-C to cancel)."
        read -r _
        run topicDiscovery/filter_sportsbetting_poker.py \
            --input "paper_to_gambling_topic_run${prev}.csv" --output "cluster_prep_run${n}.csv"
        run topicDiscovery/topicExtract.py \
            --input "cluster_prep_run${n}.csv" --text-column Document \
            --topics-output "discovered_gambling_topics_run${n}.csv" \
            --docs-output "paper_to_gambling_topic_run${n}.csv"
        ;;
    *)
        sed -n '2,11p' "$0"; exit 1 ;;
esac
log "Interactive maps: $DATA_DIR/gambling_domain_map.html, gambling_hierarchy.html"
