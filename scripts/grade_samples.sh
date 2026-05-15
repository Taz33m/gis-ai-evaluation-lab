#!/usr/bin/env bash
set -euo pipefail

python -m gis_ai_evaluation_lab grade \
  --tasks data/task_bank.json \
  --responses data/sample_ai_responses.json \
  --format markdown
