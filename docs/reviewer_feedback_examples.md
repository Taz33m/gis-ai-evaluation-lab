# Reviewer Feedback Examples

## Example 1: QuickOSM Shortcut

**AI answer:** "Run QuickOSM, export shapefiles, and you are done."

**Reviewer decision:** Reject.

**Feedback:** The answer is incomplete for a production QGIS workflow. It should include source selection, CRS handling, clipping, schema normalization, geometry/topology validation, uncertainty flags, and documented exports. QuickOSM is only an input step, not a QA process.

## Example 2: CRS Answer

**AI answer:** "Use EPSG:4326 because GeoJSON uses latitude and longitude."

**Reviewer decision:** Needs revision.

**Feedback:** The export point is reasonable, but the answer ignores local editing and measurement. For Lower Manhattan, a projected CRS such as EPSG:2263 is more appropriate for editing, measuring, and topology checks. EPSG:4326 is useful for web export, not necessarily for the working project.

## Example 3: OSM Sidewalk Completeness

**AI answer:** "OSM sidewalks are complete if the query returns features."

**Reviewer decision:** Reject.

**Feedback:** Query results do not prove completeness. OSM coverage varies by area and mapper behavior. The workflow should flag uncertain sidewalk and crossing features for review against imagery or authoritative pedestrian data before using them as ground truth.

## Example 4: Strong Schema Answer

**AI answer:** "Include source, source_id, confidence, review_status, qa_flag, notes, and last_updated so downstream users can filter reviewed features from approximate or source-derived candidates."

**Reviewer decision:** Approve.

**Feedback:** This answer correctly connects schema design to provenance, uncertainty, and downstream AI/data review needs.
