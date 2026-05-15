# Failure Taxonomy

Common failure modes in AI answers about QGIS and GIS data workflows.

## CRS Errors

- Recommends EPSG:4326 for local measurement or editing without caveats.
- Ignores projection choice entirely.
- Fails to distinguish working CRS from export CRS.

## QA Shortcuts

- Says to export after download without geometry validation.
- Treats visual inspection as enough for production readiness.
- Omits topology checks when the task involves networks or mutually exclusive polygons.

## Source Overconfidence

- Treats OSM as complete ground truth.
- Fails to preserve attribution or license obligations.
- Does not distinguish official, crowd-sourced, and manually interpreted data.

## Schema Thinness

- Uses only labels and geometry.
- Omits confidence, review status, source IDs, and QA notes.
- Makes uncertain features indistinguishable from reviewed ground truth.

## Tool Name Dropping

- Mentions QuickOSM, Geometry Checker, or Processing Toolbox without explaining when or why to use them.
- Lists tools but does not describe the workflow order.

## Reviewer Feedback Failure

- Gives generic feedback such as "good job" or "be more detailed."
- Does not identify the specific risk in the AI answer.
- Does not tell the model what a correct answer should include.
