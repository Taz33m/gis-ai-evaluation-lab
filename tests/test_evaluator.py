import unittest

from gis_ai_evaluation_lab.evaluator import band_for_score, grade_response


class EvaluatorTests(unittest.TestCase):
    def test_band_thresholds(self) -> None:
        self.assertEqual(band_for_score(9, 10), "strong")
        self.assertEqual(band_for_score(7, 10), "acceptable")
        self.assertEqual(band_for_score(5, 10), "needs_revision")
        self.assertEqual(band_for_score(3, 10), "fail")

    def test_grade_response_rewards_expected_concepts(self) -> None:
        task = {
            "id": "crs",
            "max_score": 10,
            "expected_concepts": [
                {"label": "local CRS", "terms": ["EPSG:2263", "projected CRS"]},
                {"label": "web export", "terms": ["EPSG:4326", "GeoJSON"]},
            ],
            "red_flags": [],
        }
        response = {
            "id": "answer",
            "answer": "Use EPSG:2263 as a projected CRS for editing, then EPSG:4326 for GeoJSON export.",
        }

        result = grade_response(task, response)

        self.assertEqual(result.score, 10)
        self.assertEqual(result.band, "strong")
        self.assertEqual(result.missed_expectations, [])

    def test_grade_response_penalizes_red_flags(self) -> None:
        task = {
            "id": "osm",
            "max_score": 10,
            "expected_concepts": [
                {"label": "review", "terms": ["review", "imagery"]},
                {"label": "uncertainty", "terms": ["confidence", "needs_review"]},
            ],
            "red_flags": [
                {"label": "ground truth overclaim", "terms": ["complete ground truth"]},
            ],
        }
        response = {
            "id": "bad",
            "answer": "The OSM result is complete ground truth and does not need review.",
        }

        result = grade_response(task, response)

        self.assertIn("ground truth overclaim", result.triggered_red_flags)
        self.assertLess(result.score, result.max_score)
        self.assertNotEqual(result.band, "strong")


if __name__ == "__main__":
    unittest.main()
