#!/usr/bin/env bash
# Execute a single notebook in an isolated temporary venv.
# Usage: run-notebook.sh NOTEBOOK_PATH [TIMEOUT_SECONDS]
set -euo pipefail

NOTEBOOK="${1:?Usage: run-notebook.sh NOTEBOOK_PATH [TIMEOUT_SECONDS]}"
TIMEOUT="${2:-600}"

# XGBoost on macOS needs libomp (brew install libomp).
if [[ "$(uname -s)" == "Darwin" && -d /opt/homebrew/opt/libomp/lib ]]; then
  export DYLD_LIBRARY_PATH="/opt/homebrew/opt/libomp/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
fi

# Override local hub config (~/.biolm/config.yaml) during CI-style notebook tests.
export BIOLM_BASE_API_URL="${BIOLM_BASE_API_URL:-https://biolm.ai/api/v3}"

# Prefer BIOLM_TOKEN; accept deprecated BIOLMAI_TOKEN.
if [[ -z "${BIOLM_TOKEN:-}" && -n "${BIOLMAI_TOKEN:-}" ]]; then
  export BIOLM_TOKEN="$BIOLMAI_TOKEN"
fi

if [[ -z "${BIOLM_TOKEN:-}" ]]; then
  # biolm-sdk 1.0.0 reads OAuth from ~/.biolmai/credentials; bridge ~/.biolm if needed.
  if [[ -f "${HOME}/.biolm/credentials" && ! -f "${HOME}/.biolmai/credentials" ]]; then
    mkdir -p "${HOME}/.biolmai"
    ln -sf "${HOME}/.biolm/credentials" "${HOME}/.biolmai/credentials"
  fi
  # Fall back to logged-in OAuth credentials (~/.biolm or ~/.biolmai).
  if [[ -f "${HOME}/.biolm/credentials" || -f "${HOME}/.biolmai/credentials" ]]; then
    echo "NOTE: BIOLM_TOKEN unset; using OAuth credentials for API auth."
    echo "      Pipeline notebooks still require BIOLM_TOKEN for their Setup guard."
  else
    echo "ERROR: BIOLM_TOKEN is not set and no biolm credentials found." >&2
    echo "  export BIOLM_TOKEN=your-token-here" >&2
    echo "  Get one at https://biolm.ai/ui/accounts/user-api-tokens/" >&2
    echo "  Or run: biolm login" >&2
    exit 1
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
CONTENT_DIR="$REPO_ROOT/content"

# Prefer newer Python for notebook deps (jupyterlite pins need 3.10+ in CI).
PYTHON_BIN=""
for candidate in python3.12 python3.11 python3.10 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON_BIN="$candidate"
    break
  fi
done
if [[ -z "$PYTHON_BIN" ]]; then
  echo "ERROR: No python3 interpreter found." >&2
  exit 1
fi

# Resolve notebook path
if [[ "$NOTEBOOK" = /* ]]; then
  NB_PATH="$NOTEBOOK"
else
  NB_PATH="$REPO_ROOT/$NOTEBOOK"
fi

if [[ ! -f "$NB_PATH" ]]; then
  echo "ERROR: Notebook not found: $NB_PATH" >&2
  exit 1
fi

NB_NAME="$(basename "$NB_PATH")"
NB_STEM="${NB_NAME%.ipynb}"

TMPDIR="$(mktemp -d)"
VENV="$TMPDIR/venv"
cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

echo "Creating isolated venv in $TMPDIR (using $PYTHON_BIN) ..."
"$PYTHON_BIN" -m venv "$VENV"
# shellcheck source=/dev/null
source "$VENV/bin/activate"
pip install -q --upgrade pip

# biolm-sdk 1.0 is on TestPyPI; pull deps from production PyPI.
echo "Installing biolm-sdk from TestPyPI ..."
pip install -q -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ "biolm-sdk[pipeline]"

echo "Installing notebook runtime dependencies ..."
pip install -q \
  biopython requests matplotlib numpy six py3Dmol pandas scikit-learn seaborn xgboost biotite

# Notebook execution deps
pip install -q jupyter nbconvert ipykernel nbclient
KERNEL_NAME="biolm-guide-test"
export JUPYTER_PATH="$VENV/share/jupyter"
"$VENV/bin/python" -m ipykernel install --name="$KERNEL_NAME" --display-name="BioLM Guide Test" --prefix="$VENV"

echo "Executing $NB_NAME (timeout=${TIMEOUT}s) ..."
cd "$CONTENT_DIR"
OUTPUT="/tmp/${NB_STEM}-executed.ipynb"

if jupyter nbconvert \
  --to notebook \
  --execute \
  --ExecutePreprocessor.timeout="$TIMEOUT" \
  --ExecutePreprocessor.kernel_name="$KERNEL_NAME" \
  --output "$OUTPUT" \
  "$NB_NAME"; then
  echo "PASS: $NB_NAME"
  echo "Output written to $OUTPUT (not committed)"
  exit 0
else
  echo "FAIL: $NB_NAME" >&2
  exit 1
fi
