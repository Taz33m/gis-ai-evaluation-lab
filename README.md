# GIS AI Evaluation Lab

Flagship portfolio project for evaluating AI answers to practical QGIS and geospatial data workflows.

This repo is built for GIS AI trainer/evaluator work: writing geospatial prompts, defining gold-standard expectations, spotting flawed AI reasoning, and giving clear reviewer feedback. It pairs with the companion QGIS asset project:

<https://github.com/Taz33m/qgis-ai-geospatial-assets>

## Why This Exists

Many AI answers to GIS questions sound confident while skipping the details that matter in production: CRS choice, geometry repair, source licensing, topology, export formats, uncertainty flags, and human review. This project turns those requirements into a small evaluation system.

It is not a benchmark of model intelligence. It is a reviewer toolkit for deciding whether an AI answer is useful, incomplete, risky, or wrong in real QGIS workflows.

## What Is Included

- A structured task bank with QGIS/GIS prompts, expected answer points, red flags, and scoring focus.
- A scoring rubric for CRS, geometry QA, topology, schema/provenance, exports, and AI response review.
- A failure taxonomy for common GIS AI mistakes.
- Reviewer feedback examples showing how to critique weak answers.
- A deterministic grading CLI for sample responses.
- Unit tests for the scoring behavior.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m gis_ai_evaluation_lab grade --tasks data/task_bank.json --responses data/sample_ai_responses.json
python -m unittest discover -s tests
```

No API keys are required. The grader is intentionally deterministic so the repo can be reviewed, tested, and run offline.

## Example

```bash
python -m gis_ai_evaluation_lab grade \
  --tasks data/task_bank.json \
  --responses data/sample_ai_responses.json \
  --format markdown
```

The CLI emits a concise reviewer report with:

- score
- pass/fail band
- matched expected concepts
- triggered red flags
- feedback notes

## Project Shape

```text
data/
  task_bank.json
  sample_ai_responses.json
docs/
  evaluation_rubric.md
  failure_taxonomy.md
  reviewer_feedback_examples.md
src/gis_ai_evaluation_lab/
  evaluator.py
  cli.py
tests/
  test_evaluator.py
```

## Evaluation Philosophy

Good GIS answers should be:

- **Spatially grounded:** mention CRS, measurement implications, geometry type, and layer context when relevant.
- **Operational:** describe concrete QGIS tools or workflow steps, not vague advice.
- **Source-aware:** distinguish official data, OSM-derived data, and manual interpretation.
- **QA-oriented:** validate geometry/topology and document uncertainty.
- **Reviewer-friendly:** call out assumptions, limits, and what should be checked before treating data as ground truth.

## Companion Projects

This is intended as the second flagship project in a three-project portfolio:

1. **AI-Ready Lower Manhattan QGIS Portfolio**: production-style GIS asset package.
2. **GIS AI Evaluation Lab**: AI answer evaluation toolkit for QGIS/GIS workflows.
3. **RPInSight**: tangential product showing geospatial app UX, campus search, and Mapbox integration.
