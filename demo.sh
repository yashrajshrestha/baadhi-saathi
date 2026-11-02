#!/usr/bin/env bash
# One-command demo: ./demo.sh [place] [ne|en]
set -euo pipefail
cd "$(dirname "$0")"
VENV="${VENV:-$HOME/sample-strands-agents-hands-on-workshop/.venv}"
[ -f "$VENV/bin/activate" ] && source "$VENV/bin/activate"
export AWS_PROFILE="${AWS_PROFILE:-personal}" AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
exec python3 -m saathi.agent "${1:-Arughat}" --lang "${2:-ne}" --show-steps
