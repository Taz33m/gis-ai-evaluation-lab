# Evaluation Rubric

Use this rubric to review AI-generated answers for QGIS and geospatial data production tasks.

## Scoring Bands

| Band | Score Ratio | Reviewer Meaning |
|---|---:|---|
| `strong` | 85-100% | Approve or lightly edit. The answer is operational and safe. |
| `acceptable` | 65-84% | Mostly correct but missing useful detail. Request a targeted improvement. |
| `needs_revision` | 40-64% | Do not approve without revisions. Important workflow pieces are missing. |
| `fail` | 0-39% | Reject. The answer is misleading, unsafe, or too vague. |

## Core Criteria

### CRS and Measurement

Strong answers explain why a local projected CRS is appropriate for editing, measurement, and topology checks, and why EPSG:4326 is common for web GeoJSON export.

Weak answers treat all coordinate systems as interchangeable or recommend WGS84 for every operation.

### Geometry and Topology QA

Strong answers name concrete checks: geometry validity, duplicate geometries, polygon overlaps/gaps, network connectivity, and layer-specific topology rules.

Weak answers say to export immediately or rely on visual inspection only.

### Source and License Awareness

Strong answers distinguish official sources, OSM, and manual interpretation. They preserve attribution and explain source limitations.

Weak answers treat all downloaded data as authoritative.

### Schema and Review State

Strong answers include provenance, confidence, `review_status`, `qa_flag`, and notes for uncertain features.

Weak answers keep only labels and ignore downstream review workflows.

### Reviewer Feedback Quality

Strong feedback is specific, actionable, and tied to GIS risk. It says what is missing and how to fix it.

Weak feedback is generic praise or vague criticism.
