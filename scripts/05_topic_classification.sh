#!/usr/bin/env bash
# Stage 5 - Label every corpus paper with one AI topic, one gambling topic and (for
# Sports Betting papers) one sport, then join everything into the analysis file.
#   in:  filtered_openalex_works.csv
#   out: ai_gambling_corpus.csv
source "$(dirname "$0")/common.sh"
require_ollama deepseek-r1:14b
require_file filtered_openalex_works.csv

run topicClassification/AITopicClassifier.py \
    --input filtered_openalex_works.csv --output ai_topic_classified_papers.csv
run topicClassification/gamblingTopicClassifier.py \
    --input filtered_openalex_works.csv --output gambling_topic_classified_papers.csv
run topicClassification/setupSportsBettingCSV.py \
    --input gambling_topic_classified_papers.csv --output sports_betting_papers.csv
run topicClassification/SportsBettingTopicClassifier.py \
    --input sports_betting_papers.csv --output sports_betting_classified_by_sport.csv
run topicClassification/csv_merger.py \
    --main filtered_openalex_works.csv \
    --gambling gambling_topic_classified_papers.csv \
    --ai ai_topic_classified_papers.csv \
    --sports sports_betting_classified_by_sport.csv \
    --output ai_gambling_corpus.csv
