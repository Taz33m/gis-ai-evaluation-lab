#!/usr/bin/env python3
"""Build a QGIS-ready GeoPackage and project for the GIS AI Evaluation Lab."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from osgeo import ogr, osr
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsApplication,
    QgsCategorizedSymbolRenderer,
    QgsCoordinateReferenceSystem,
    QgsMarkerSymbol,
    QgsProject,
    QgsRendererCategory,
    QgsVectorLayer,
)


ROOT = Path(__file__).resolve().parents[1]
TASK_BANK = ROOT / "data" / "task_bank.json"
RESPONSES = ROOT / "data" / "sample_ai_responses.json"
GPKG = ROOT / "data" / "processed" / "gis_ai_evaluation_lab.gpkg"
PROJECT_PATH = ROOT / "qgis" / "gis_ai_evaluation_lab.qgz"
CRS = "EPSG:4326"

CATEGORY_COORDS = {
    "CRS and export": (-74.0145, 40.7132),
    "Geometry QA": (-74.0118, 40.7127),
    "Topology": (-74.0097, 40.7138),
    "OSM interpretation": (-74.0136, 40.7160),
    "Schema and provenance": (-74.0109, 40.7153),
    "Packaging and exports": (-74.0161, 40.7116),
    "AI response review": (-74.0079, 40.7119),
    "Feature ambiguity": (-74.0124, 40.7099),
    "Joins and attributes": (-74.0064, 40.7145),
    "Spatial joins": (-74.0150, 40.7087),
    "Field calculator": (-74.0088, 40.7090),
    "Raster/vector reasoning": (-74.0068, 40.7164),
    "Map layout": (-74.0172, 40.7141),
    "Processing workflow": (-74.0048, 40.7129),
    "Licensing and attribution": (-74.0181, 40.7103),
    "Metadata": (-74.0057, 40.7105),
    "Geoprocessing": (-74.0039, 40.7155),
    "Symbology": (-74.0187, 40.7162),
    "Packaging": (-74.0195, 40.7125),
    "AI training data": (-74.0029, 40.7117),
    "Reviewer communication": (-74.0043, 40.7087),
    "Automation": (-74.0205, 40.7149),
    "Spatial filtering": (-74.0018, 40.7138),
    "POI normalization": (-74.0208, 40.7091),
}

CATEGORY_COLORS = {
    "CRS and export": "#2f80ed",
    "Geometry QA": "#eb5757",
    "Topology": "#f2994a",
    "OSM interpretation": "#27ae60",
    "Schema and provenance": "#9b51e0",
    "Packaging and exports": "#56ccf2",
    "AI response review": "#f2c94c",
    "Feature ambiguity": "#ff5d8f",
    "Geoprocessing": "#00a896",
}


def load_inputs() -> tuple[list[dict], list[dict]]:
    tasks = json.loads(TASK_BANK.read_text(encoding="utf-8"))["tasks"]
    responses = json.loads(RESPONSES.read_text(encoding="utf-8"))["responses"]
    return tasks, responses


def create_field(layer: ogr.Layer, name: str, field_type: int = ogr.OFTString, width: int = 254) -> None:
    field = ogr.FieldDefn(name, field_type)
    if field_type == ogr.OFTString:
        field.SetWidth(width)
    layer.CreateField(field)


def set_feature_fields(feature: ogr.Feature, values: dict[str, object]) -> None:
    for key, value in values.items():
        if value is None:
            continue
        feature.SetField(key, str(value) if not isinstance(value, int) else value)


def create_geopackage(tasks: list[dict], responses: list[dict]) -> None:
    GPKG.parent.mkdir(parents=True, exist_ok=True)
    if GPKG.exists():
        GPKG.unlink()

    driver = ogr.GetDriverByName("GPKG")
    ds = driver.CreateDataSource(str(GPKG))
    if ds is None:
        raise RuntimeError(f"Could not create {GPKG}")

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    task_points = ds.CreateLayer("evaluation_task_anchors", srs, ogr.wkbPoint)
    for name, typ, width in [
        ("task_id", ogr.OFTString, 32),
        ("category", ogr.OFTString, 96),
        ("prompt", ogr.OFTString, 1024),
        ("max_score", ogr.OFTInteger, 0),
        ("expected_count", ogr.OFTInteger, 0),
        ("red_flag_count", ogr.OFTInteger, 0),
        ("review_focus", ogr.OFTString, 512),
    ]:
        create_field(task_points, name, typ, width)

    category_offsets: dict[str, int] = {}
    for task in tasks:
        lon, lat = CATEGORY_COORDS.get(task["category"], (-74.01, 40.7128))
        offset = category_offsets.get(task["category"], 0)
        category_offsets[task["category"]] = offset + 1
        lon += (offset % 3) * 0.00045
        lat += (offset // 3) * 0.00035

        feature = ogr.Feature(task_points.GetLayerDefn())
        feature.SetGeometry(ogr.CreateGeometryFromWkt(f"POINT ({lon} {lat})"))
        set_feature_fields(
            feature,
            {
                "task_id": task["id"],
                "category": task["category"],
                "prompt": task["prompt"],
                "max_score": task["max_score"],
                "expected_count": len(task["expected_concepts"]),
                "red_flag_count": len(task["red_flags"]),
                "review_focus": ", ".join(item["label"] for item in task["expected_concepts"][:3]),
            },
        )
        task_points.CreateFeature(feature)

    ds = None

    with sqlite3.connect(GPKG) as conn:
        conn.executescript(
            """
            CREATE TABLE evaluation_tasks (
                task_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                prompt TEXT NOT NULL,
                max_score INTEGER NOT NULL
            );
            CREATE TABLE expected_concepts (
                task_id TEXT NOT NULL,
                concept_label TEXT NOT NULL,
                terms TEXT NOT NULL
            );
            CREATE TABLE red_flags (
                task_id TEXT NOT NULL,
                red_flag_label TEXT NOT NULL,
                terms TEXT NOT NULL
            );
            CREATE TABLE sample_ai_responses (
                response_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                answer TEXT NOT NULL
            );
            """
        )
        for task in tasks:
            conn.execute(
                "INSERT INTO evaluation_tasks VALUES (?, ?, ?, ?)",
                (task["id"], task["category"], task["prompt"], task["max_score"]),
            )
            for concept in task["expected_concepts"]:
                conn.execute(
                    "INSERT INTO expected_concepts VALUES (?, ?, ?)",
                    (task["id"], concept["label"], "; ".join(concept["terms"])),
                )
            for flag in task["red_flags"]:
                conn.execute(
                    "INSERT INTO red_flags VALUES (?, ?, ?)",
                    (task["id"], flag["label"], "; ".join(flag["terms"])),
                )
        for response in responses:
            conn.execute(
                "INSERT INTO sample_ai_responses VALUES (?, ?, ?)",
                (response["id"], response["task_id"], response["answer"]),
            )

        for table, description in [
            ("evaluation_tasks", "QGIS/GIS AI evaluation prompts and task metadata"),
            ("expected_concepts", "Gold-standard concepts expected in strong answers"),
            ("red_flags", "Risk signals that should reduce reviewer confidence"),
            ("sample_ai_responses", "Sample AI answers for deterministic grading examples"),
        ]:
            conn.execute(
                """
                INSERT OR REPLACE INTO gpkg_contents
                    (table_name, data_type, identifier, description, last_change)
                VALUES (?, 'attributes', ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                """,
                (table, table, description),
            )


def style_task_layer(layer: QgsVectorLayer) -> None:
    categories: list[QgsRendererCategory] = []
    seen = sorted({feature["category"] for feature in layer.getFeatures()})
    palette = [
        "#2f80ed",
        "#eb5757",
        "#f2994a",
        "#27ae60",
        "#9b51e0",
        "#56ccf2",
        "#f2c94c",
        "#ff5d8f",
        "#00a896",
        "#f26419",
    ]
    for index, category in enumerate(seen):
        color = CATEGORY_COLORS.get(category, palette[index % len(palette)])
        symbol = QgsMarkerSymbol.createSimple(
            {
                "name": "circle",
                "color": color,
                "outline_color": "#111111",
                "outline_width": "0.2",
                "size": "4.0",
                "size_unit": "MM",
            }
        )
        categories.append(QgsRendererCategory(category, symbol, category))
    layer.setRenderer(QgsCategorizedSymbolRenderer("category", categories))


def create_qgis_project() -> None:
    PROJECT_PATH.parent.mkdir(parents=True, exist_ok=True)

    qgs = QgsApplication([], False)
    qgs.initQgis()
    try:
        project = QgsProject.instance()
        project.clear()
        project.setCrs(QgsCoordinateReferenceSystem(CRS))
        project.writeEntry("Paths", "/Absolute", False)
        project.setTitle("GIS AI Evaluation Lab")

        layers = [
            ("evaluation_task_anchors", "Evaluation Task Anchors"),
            ("evaluation_tasks", "Evaluation Tasks"),
            ("expected_concepts", "Expected Concepts"),
            ("red_flags", "Red Flags"),
            ("sample_ai_responses", "Sample AI Responses"),
        ]
        loaded = []
        for table_name, display_name in layers:
            layer = QgsVectorLayer(f"{GPKG}|layername={table_name}", display_name, "ogr")
            if not layer.isValid():
                raise RuntimeError(f"Could not load {table_name}")
            if table_name == "evaluation_task_anchors":
                style_task_layer(layer)
            project.addMapLayer(layer)
            loaded.append(layer)

        root = project.layerTreeRoot()
        root.setHasCustomLayerOrder(True)
        root.setCustomLayerOrder(loaded)

        if not project.write(str(PROJECT_PATH)):
            raise RuntimeError(f"Could not write {PROJECT_PATH}")
    finally:
        qgs.exitQgis()


def main() -> None:
    tasks, responses = load_inputs()
    create_geopackage(tasks, responses)
    create_qgis_project()
    print(f"Wrote {GPKG}")
    print(f"Wrote {PROJECT_PATH}")


if __name__ == "__main__":
    main()
