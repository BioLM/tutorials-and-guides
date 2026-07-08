#!/usr/bin/env bash
# Execute multiple notebooks in isolated temporary venvs (one venv per notebook).
# Usage: run-notebooks.sh PATTERN|--all [TIMEOUT_SECONDS]
#   PATTERN is a glob relative to content/ (e.g. "10.*")
set -euo pipefail

PATTERN="${1:?Usage: run-notebooks.sh PATTERN|--all [TIMEOUT_SECONDS]}"
TIMEOUT="${2:-600}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
CONTENT_DIR="$REPO_ROOT/content"
RUN_ONE="$SCRIPT_DIR/run-notebook.sh"

NOTEBOOKS=()

if [[ "$PATTERN" == "--all" ]]; then
  while IFS= read -r -d '' f; do
    NOTEBOOKS+=("$f")
  done < <(find "$CONTENT_DIR" -maxdepth 1 -name '*.ipynb' -print0 | sort -z)
else
  shopt -s nullglob
  for f in "$CONTENT_DIR"/${PATTERN}.ipynb; do
    NOTEBOOKS+=("$f")
  done
  shopt -u nullglob
fi

if [[ ${#NOTEBOOKS[@]} -eq 0 ]]; then
  echo "ERROR: No notebooks matched: $PATTERN" >&2
  exit 1
fi

echo "Running ${#NOTEBOOKS[@]} notebook(s) ..."
FAILED=0
for nb in "${NOTEBOOKS[@]}"; do
  rel="content/$(basename "$nb")"
  if ! "$RUN_ONE" "$rel" "$TIMEOUT"; then
    FAILED=$((FAILED + 1))
  fi
  echo "---"
done

if [[ $FAILED -gt 0 ]]; then
  echo "FAILED: $FAILED / ${#NOTEBOOKS[@]} notebook(s)" >&2
  exit 1
fi

echo "PASS: all ${#NOTEBOOKS[@]} notebook(s)"
