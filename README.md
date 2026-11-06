# AI in Gambling Research: Publication Mapping Pipeline

Code for a bibliometric map of artificial-intelligence research in gambling studies,
2010-2025. The pipeline collects candidate papers from [OpenAlex](https://openalex.org),
filters them with a locally run LLM into a corpus of AI + gambling papers (899 in the
published run), labels each paper by AI topic, gambling topic and sport, and produces
the figures.

Everything runs locally. The LLM steps use [Ollama](https://ollama.com), so no paid API
or API key is needed. This repository contains code only; running it creates all data.

- **[PIPELINE.md](PIPELINE.md)**: what each stage does and the published counts
- **[PROMPTS.txt](PROMPTS.txt)**: the search terms and every classifier prompt

---

## Quickstart

### 1. Requirements

| | |
|---|---|
| OS | Linux or macOS (tested on Ubuntu Linux) |
| Python | 3.8 (tested with 3.8.20) |
| Ollama | any recent version, with `deepseek-r1:14b` and `qwen3:14b` |
| GPU | strongly recommended: a 14B model needs about 10 GB of GPU memory (tested on a 20 GB NVIDIA RTX 4000 Ada). CPU-only works but is far slower. |
| Disk | about 6 GB for the Python packages, 19 GB for the two models, 0.5 GB for the embedding model (downloaded on first use) and about 1 GB for data |

### 2. Install

```bash
git clone <this repository URL>
cd <repository folder>

python3.8 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you do not have Python 3.8, [pyenv](https://github.com/pyenv/pyenv) can install it:
`pyenv install 3.8.20`.

### 3. Set up Ollama

Install Ollama from <https://ollama.com/download>, then:

```bash
ollama serve &                 # skip if the Ollama app is already running
ollama pull deepseek-r1:14b    # all classifiers
ollama pull qwen3:14b          # topic discovery only
```

If Ollama runs on another machine or port, set `OLLAMA_HOST`, for example
`export OLLAMA_HOST=http://gpu-box:11434`.

### 4. Get an OpenAlex API key

OpenAlex needs a **free API key** for any query that returns more than one page of
results, so stage 1 cannot run without one. Create a key at
<https://openalex.org/settings/api>, then set it along with your contact email:

```bash
export OPENALEX_API_KEY="your-key"
export OPENALEX_EMAIL="you@your-institution.edu"
```

A free key includes a daily usage allowance ($1/day at the time of writing). A full
run uses only a small part of it: list queries cost about $0.0001 per page of 200
results, and single-paper lookups are free.

### 5. Run

```bash
./scripts/run_all.sh
```

All output goes to `data/`. Figures end up in `data/figures/`. The full run takes
days on a single GPU (see [Runtime](#runtime)), so start it inside `tmux` or `screen`.

---

## Usage guide

### Stages

`run_all.sh` runs six stage scripts in order. Each can also be run on its own.

| Stage | Script | What it does | Main output |
|---|---|---|---|
| 1 | `scripts/01_capture.sh` | Query OpenAlex by search terms and by topic ID, then merge | `master_gambling_dataset.json` |
| 2 | `scripts/02_ai_filter.sh` | LLM: is the paper AI-related? Re-fetch title and abstract for AI-true papers | `attempt_2_postAIClassifcation.json` |
| 3 | `scripts/03_gambling_filter.sh` | LLM: is the paper gambling-related? Run on the AI-true papers (corpus) and on the full dataset (denominator) | `master_gambling_classification.json`, `just_gambling_publications.csv` |
| 4 | `scripts/04_build_corpus.sh` | Fetch full OpenAlex metadata (affiliations, venue, citations), then **manual review** | `filtered_openalex_works.csv` |
| 5 | `scripts/05_topic_classification.sh` | LLM: one AI topic, one gambling topic and one sport per paper, then merge | `ai_gambling_corpus.csv` |
| 6 | `scripts/06_visualize.sh` | All figures and summary tables | `figures/*.png` |
| - | `scripts/topic_discovery.sh` | Optional and exploratory: BERTopic clustering (see [below](#topic-discovery-optional)) | `discovered_gambling_topics_run*.csv` |

Each stage checks that its input exists and that Ollama and the model are available
before it starts.

### Running part of the pipeline

```bash
./scripts/run_all.sh --from 4          # resume at stage 4
./scripts/run_all.sh --from 2 --to 3   # only stages 2 and 3
./scripts/05_topic_classification.sh   # a single stage
```

The LLM classifiers save progress as they go (every 10-20 papers). If one is
interrupted, re-running the same stage resumes it. To start a classifier over,
delete its output file from `data/`.

### The manual review step (after stage 4)

OpenAlex indexes some spam: in the published run, 9 of the 908 corpus candidates were
pirated sports live-stream pages (titles like *"Miami Dolphins vs Pittsburgh Steelers
Live Free Online TV Broadcast"*). The pipeline does not filter these automatically.
After stage 4, open `data/filtered_openalex_works.csv`, delete any rows that are not
research publications, and save the file under the same name. When run from a
terminal, `run_all.sh` pauses here until you press Enter.

### Settings

All settings are environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `OPENALEX_API_KEY` | *(unset)* | Your free OpenAlex API key. Required for stage 1 and recommended for stages 2-4. |
| `OPENALEX_EMAIL` | *(unset)* | Your contact email for OpenAlex |
| `OLLAMA_HOST` | `http://localhost:11434` | Where the Ollama server is |
| `PYTHON` | `python` | Python interpreter to use, e.g. `.venv/bin/python` |
| `DATA_DIR` | `./data` | Where all inputs and outputs are read and written |
| `SKIP_DENOMINATOR` | `0` | Set to `1` to skip the full-dataset gambling run in stage 3. That run is the slowest step; without it, `percentAIInGambling.py` is skipped. |

### Running a script by hand

Every Python script takes `--input`/`--output` options (`--help` lists them), and
reads and writes files in the current directory. The stage scripts show the exact
commands used. For example:

```bash
cd data
python ../classifiers/binaryAIClassification.py \
    --input master_gambling_dataset.json --output master_ai_classification.json
```

### Topic discovery (optional)

The topic lists used in stage 5 were found with BERTopic. This step is exploratory:
it needs human judgement, and nothing downstream reads its output. The final lists are
written into the stage 5 prompts. To repeat it after stage 4:

```bash
./scripts/topic_discovery.sh first       # cluster the whole corpus
./scripts/topic_discovery.sh refine 2    # drop resolved topics, re-cluster the rest
./scripts/topic_discovery.sh refine 3    # ...and so on
```

**You will need to tune it.** `min_topic_size` in `topicDiscovery/topicExtract.py`
sets how coarse the clusters are. It was adjusted by hand between runs until the
clusters were interpretable, and there is no single correct value. Before each
`refine`, edit the topic numbers in `topicDiscovery/filter_sportsbetting_poker.py`
to the topics you want to drop from the previous run, because topic numbers differ
between runs. Each run also writes interactive maps (`gambling_domain_map.html`,
`gambling_hierarchy.html`) to `data/`.

---

## Runtime

The LLM stages dominate. `deepseek-r1:14b` reasons before it answers, so each paper
takes about 8-11 seconds on one NVIDIA RTX 4000 Ada (20 GB). Estimates at the
published dataset sizes:

| Step | Papers | Per paper | Approx. time |
|---|---|---|---|
| Stage 2: AI classifier | 103,736 | ~8 s | **~9-10 days** |
| Stage 3: gambling classifier on AI-true papers | 6,755 | ~9 s | ~17 hours |
| Stage 3b: gambling classifier on the full dataset | 103,736 | ~9 s | **~10 days** (skip with `SKIP_DENOMINATOR=1`) |
| Stage 5: AI, gambling and sport topics | 899 + 899 + ~245 | 8-11 s | ~5-6 hours |

Stages 1 and 4 are limited by OpenAlex response times and take minutes to an hour or
so. Stage 6 takes about a minute. A faster GPU shortens the LLM stages.

---

## What to expect when you re-run it

Your numbers will not exactly match the published ones:

- **OpenAlex changes.** New papers are indexed, records are merged, and topics are
  reassigned over time, so stage 1 returns a different set of papers than in the
  published run (103,736). For example, in November 2026 the topic query returned
  31,801 papers, compared with 48,245 in the published run.
- **LLM output varies slightly between runs**, even at `temperature=0.0`. See the
  reproducibility notes in [PIPELINE.md](PIPELINE.md#reproducibility-notes).
- **Some OpenAlex fetches can fail** in stage 2. `missingEntries.py` reports them at
  the end of the stage. Re-running stage 2's fetch step usually recovers them.

The published counts for each stage are in [PIPELINE.md](PIPELINE.md).

---

## Repository layout

```
initialCapture/        stage 1: OpenAlex queries and merge
classifiers/           stages 2-3: binary AI and gambling classifiers
corpusBuilding/        stages 3b-4: metadata enrichment
topicClassification/   stage 5: topic classifiers and merge
topicDiscovery/        optional: BERTopic topic discovery
visualizations/        stage 6: figures and tables
scripts/               shell runners for each stage
legacy/                kept for the record, not used
PIPELINE.md            method notes and published counts
PROMPTS.txt            search terms and classifier prompts
requirements.txt       pinned Python dependencies
```
