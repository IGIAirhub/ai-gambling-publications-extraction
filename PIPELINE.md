# AI in Gambling Research: Pipeline Method Notes

This document describes what each stage does and what the published run produced.
For installing and running the pipeline, see [README.md](README.md).

All LLM steps run locally through **Ollama** with `temperature=0.0`. Every
classifier (binary and topic) uses **`deepseek-r1:14b`**; BERTopic cluster naming
uses **`qwen3:14b`**. The full prompt text for every classifier is in
[PROMPTS.txt](PROMPTS.txt).

The scripts are the ones used for the published analysis. The only changes are
`--input`/`--output` command-line options, whose defaults are the original
hard-coded file names, and OpenAlex credentials, which are now read from the
`OPENALEX_EMAIL` and `OPENALEX_API_KEY` environment variables.

---

## Flow

```
                    OpenAlex API
                         |
        +----------------+----------------+
        |                                 |
  terms query                       topics query                 Stage 1
  (27 search terms)              (T11674, T11705)
  query_by_terms.json            query_by_topics.json
      69,908                          48,245
        |                                 |
        +----------------+----------------+
                         |  dataset_merger.py  (14,417 overlap removed)
              master_gambling_dataset.json
                       103,736
                         |
                         |  binaryAIClassification.py                      Stage 2
              master_ai_classification.json
                    6,769 AI-true
                         |  postAIClassifcation.py  (re-attach title + abstract)
           attempt_2_postAIClassifcation.json
                 6,755  (14 fetches failed)
                         |
                         |  binaryGamblingClassification.py                Stage 3
            master_gambling_classification.json
                      908 true
                         |
                         |  dataAnalysis.py  (re-query OpenAlex)           Stage 4
                         |  + manual removal of 9 streaming-spam pages
                filtered_openalex_works.csv
                       899 papers              <-- THE CORPUS
                         |
                         |  AI / gambling / sport topic classifiers       Stage 5
                         |  csv_merger.py
                   ai_gambling_corpus.csv
                         |
                    visualizations/                                        Stage 6

  Side branch (Stage 3b), the denominator:
  master_gambling_dataset.json -> binaryGamblingClassification.py
      -> gambling_classifier_on_master.json (29,952 true)
      -> extractGamblingPaperYears.py -> just_gambling_publications.csv
      -> percentAIInGambling.py

  Exploratory, not in the chain: topicDiscovery/ (BERTopic) found the label
  lists that the Stage 5 prompts use.
```

---

## Stage 1: Initial capture (`initialCapture/`)

Two independent OpenAlex queries, then a merge. Both are limited to 2010-01-01 to
2025-12-31, English, and types article, review, book-chapter and book.

| Script | Output | Published count |
|---|---|---|
| `terms_extract_gambling_publications.py` | `query_by_terms.json` | 69,908 |
| `topic_extract_gambling_publications.py` | `query_by_topics.json` | 48,245 |
| `dataset_merger.py` | `master_gambling_dataset.json` | **103,736** |

The two queries overlapped by 14,417 papers. The search terms and OpenAlex topic IDs
are listed at the top of `PROMPTS.txt`. The topic script's default output name is
`topictest.json`; in the published run this file was renamed by hand, and the runner
now passes `--output query_by_topics.json` instead.

## Stage 2: AI filter (`classifiers/`)

| Script | In | Out | Published result |
|---|---|---|---|
| `binaryAIClassification.py` | `master_gambling_dataset.json` | `master_ai_classification.json` | 6,769 of 103,736 AI-true |
| `postAIClassifcation.py` | `master_ai_classification.json` | `attempt_2_postAIClassifcation.json` | 6,755 records |
| `missingEntries.py` | both of the above | `missing_entries.json` | 14 missing |

The classifier writes only `{work_id: true/false}`. `postAIClassifcation.py`
re-fetches the title and abstract of every AI-true paper from OpenAlex so the
gambling classifier has text to read. `missingEntries.py` is an integrity check that
lists AI-true papers whose fetch failed.

In the published run, 14 fetches failed. All 14 were later classified
*not gambling-related* by the full-dataset run (Stage 3b), so leaving them out did
not change the corpus. A manual retry was attempted (`recovered_entries.json`, which
is still the script's default input) but never merged back in.

The classifiers save progress every 20 records and resume from their own output
file, so a stopped run continues where it left off.

## Stage 3: Gambling filter (`classifiers/`)

`binaryGamblingClassification.py` on `attempt_2_postAIClassifcation.json` produces
`master_gambling_classification.json`: 6,755 scored, **908 gambling-true**.

### Stage 3b: the denominator

The same classifier was also run on the *full* 103,736-paper dataset, producing
`gambling_classifier_on_master.json` with 29,952 gambling-true papers. This is not
part of the corpus chain. `corpusBuilding/extractGamblingPaperYears.py` turns it
into `just_gambling_publications.csv` (ID and year), which
`visualizations/percentAIInGambling.py` uses as the denominator for "what share of
gambling research is AI research".

## Stage 4: Corpus building (`corpusBuilding/`)

`dataAnalysis.py` takes the 908 gambling-true IDs, re-queries OpenAlex in batches of
25, and for each work:

- reconstructs the abstract from OpenAlex's inverted index
- extracts every author affiliation (institution name, country code, sector)
- extracts venue type from the nested `primary_location.source`

**Manual step.** Nine of the 908 were pirated sports live-stream pages indexed by
OpenAlex (titles like "Miami Dolphins vs Pittsburgh Steelers Live Free Online TV
Broadcast"). They were deleted from the CSV by hand. The script does not filter
them.

Output: **`filtered_openalex_works.csv`, 899 papers**, the input to everything
downstream.

## Topic discovery (`topicDiscovery/`, exploratory)

`topicExtract.py` runs BERTopic over the corpus:

- embeddings: `sentence-transformers/all-mpnet-base-v2`
- cluster names written by local **qwen3:14b** through Ollama's OpenAI-compatible
  endpoint (`http://localhost:11434/v1`), prompted to name the *gambling domain* and
  ignore the AI method
- `min_topic_size` was tuned by hand between runs until the clusters were
  interpretable. The script holds the value from the final run (10).

It was run five times. The first run clustered the whole corpus
(`title_abstract_combined`). Between runs, `filter_sportsbetting_poker.py` dropped
the topics already resolved (`-1` and `1`-`8` after the first run) so the next run
re-clustered only the sports-betting remainder at finer grain.

**This stage produced the label vocabulary, not the labels.** Its result is the
category lists written into the Stage 5 prompts. No BERTopic cluster assignment
is carried into the final corpus, and nothing downstream reads its output.

Two working lists are kept in `topicDiscovery/`. `finalTopics.txt` has 9 gambling
topics. The Stage 5 gambling prompt uses 7 of them: *Gambling Regulation* and
*Lottery* are not in it. `topics.txt` is an earlier, broader AI and gambling
taxonomy. The prompts in `topicClassification/` (and `PROMPTS.txt`) are the
definitive lists.

## Stage 5: Topic classification (`topicClassification/`)

A local LLM assigns exactly one label per paper, per dimension, from fixed lists.

| Script | Labels | Output |
|---|---|---|
| `AITopicClassifier.py` | 10 AI/ML topics | `ai_topic_classified_papers.csv` |
| `gamblingTopicClassifier.py` | 7 gambling topics | `gambling_topic_classified_papers.csv` |
| `setupSportsBettingCSV.py` | keeps Sports Betting rows | `sports_betting_papers.csv` |
| `SportsBettingTopicClassifier.py` | 11 sports | `sports_betting_classified_by_sport.csv` |
| `csv_merger.py` | joins all of the above | **`ai_gambling_corpus.csv`** |

The sport pass is a third-level drill-down: only papers already labeled *Sports
Betting* get a sport assigned.

In the published run, two outputs were renamed by hand. The defaults
`topic_classified_gambling_papers.csv` and `master_classified_works.csv` became
`gambling_topic_classified_papers.csv` and `ai_gambling_corpus.csv`. The runner now
passes those names with `--output`.

## Stage 6: Visualizations (`visualizations/`)

All read `ai_gambling_corpus.csv` unless noted.

| Script | Produces |
|---|---|
| `publicationsByYear.py`, `numberByYearVisual.py` | publication volume over time (`numberByYearVisual.py` reads `filtered_openalex_works.csv`) |
| `percentAIInGambling.py` | AI share of gambling research (also reads `just_gambling_publications.csv`) |
| `sectorVisual.py` | academic vs. industry vs. government |
| `venueTypeVisual.py` | journal / conference / repository split |
| `regionVisual.py` | geographic trends, plus `ai_gambling_with_regions.csv` |
| `citedByOrganization.py`, `top10_orgs_*.py`, `top10orgs_*.py` | institutional output and citation rankings (`citedByOrganization.py` reads `filtered_openalex_works.csv`) |
| `AITopicsVisual.py`, `GamblingTopicsVisual.py`, `sportTopicVisual.py` | topic trends |
| `extractGamblingTopicStatistic.py` | topic count table (reads `gambling_topic_classified_papers.csv`) |
| `COSINE_SIMILARITY_FOR_DOCS.py` | most representative paper per topic, written to `representative_publications.csv` |

---

## Reproducibility notes

**OpenAlex changes over time.** Re-running Stage 1 today returns a different number
of papers, as works are added, merged and re-indexed, and topics are reassigned. In
November 2026 the topic query (T11674 | T11705, same filters) returned 31,801 papers,
compared with 48,245 in the published run. All counts above are from the published
run. OpenAlex has also introduced API keys since the published run: paging through
query results now requires a free key (`OPENALEX_API_KEY`).

**LLM runs are not perfectly repeatable.** The AI-true set was scored by the gambling
classifier twice: once in Stage 3 (908 true) and once inside the full-dataset run in
Stage 3b (913 true). The two runs disagree on 149 papers: 77 are true only in the
full run and 72 only in the Stage 3 run. Same model, `temperature=0.0`. The corpus
uses the Stage 3 result.

**Unparseable responses.** `master_ai_classification.json` has 1 `null` and
`gambling_classifier_on_master.json` has 8. These are papers where the LLM returned
output that could not be parsed. They are stored as `null`, not dropped, so they can
be retried.

## Legacy

`legacy/postGamblingClassifcation.py` is an earlier copy of the title/abstract
fetch script. Its output is not read by any stage. It is kept for the record only.
