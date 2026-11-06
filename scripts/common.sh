#!/usr/bin/env bash
# Shared settings for every stage script. Sourced, not run directly.
#
# Override any of these from the environment, e.g.
#   PYTHON=.venv/bin/python DATA_DIR=/scratch/run1 ./scripts/run_all.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python}"
DATA_DIR="${DATA_DIR:-$REPO_DIR/data}"
OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
export OLLAMA_HOST
export MPLBACKEND="${MPLBACKEND:-Agg}"   # figures are saved to disk; never open a window

mkdir -p "$DATA_DIR"
# Every script reads and writes files in its current directory, so all of them run inside DATA_DIR.
cd "$DATA_DIR"

log() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
die() { printf '\033[31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

# run <path/relative/to/repo.py> [args...]
run() {
    local script="$1"; shift
    log "$script $*"
    "$PYTHON" "$REPO_DIR/$script" "$@"
}

require_file() {
    for f in "$@"; do
        [[ -s "$f" ]] || die "missing input '$DATA_DIR/$f' - run the earlier stage first."
    done
}

# require_openalex [strict]
#   strict: stop if OPENALEX_API_KEY is unset (needed for paging, i.e. stage 1)
require_openalex() {
    if [[ -z "${OPENALEX_EMAIL:-}" ]]; then
        printf '\033[33mWARNING: OPENALEX_EMAIL is not set. Set it with: export OPENALEX_EMAIL="you@example.org"\033[0m\n' >&2
    fi
    if [[ -z "${OPENALEX_API_KEY:-}" ]]; then
        local msg="OPENALEX_API_KEY is not set. Get a free key at https://openalex.org/settings/api, then: export OPENALEX_API_KEY=\"your-key\""
        [[ "${1:-}" == strict ]] && die "$msg (OpenAlex requires a key to page through query results.)"
        printf '\033[33mWARNING: %s\nWithout a key, requests share a small daily budget per IP address and may fail.\033[0m\n' "$msg" >&2
    fi
}

# require_ollama <model> [model...]
require_ollama() {
    command -v curl >/dev/null || die "curl is required to check the Ollama server."
    local tags
    tags="$(curl -fsS "$OLLAMA_HOST/api/tags")" \
        || die "Ollama is not reachable at $OLLAMA_HOST. Start it with 'ollama serve'."
    for m in "$@"; do
        grep -q "\"$m\"" <<<"$tags" || die "Ollama model '$m' is not installed. Run: ollama pull $m"
    done
}
