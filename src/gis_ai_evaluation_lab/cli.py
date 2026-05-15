from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .evaluator import EvaluationResult, grade_response


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def format_markdown(results: list[EvaluationResult]) -> str:
    lines = ["# GIS AI Evaluation Report", ""]
    for result in results:
        lines.extend(
            [
                f"## {result.response_id} on {result.task_id}",
                "",
                f"- Score: **{result.score}/{result.max_score}**",
                f"- Band: **{result.band}**",
                "- Matched: " + (", ".join(result.matched_expectations) or "none"),
                "- Missed: " + (", ".join(result.missed_expectations) or "none"),
                "- Red flags: " + (", ".join(result.triggered_red_flags) or "none"),
                "",
            ]
        )
        for note in result.feedback:
            lines.append(f"- Feedback: {note}")
        lines.append("")
    return "\n".join(lines)


def format_json(results: list[EvaluationResult]) -> str:
    return json.dumps([result.__dict__ for result in results], indent=2)


def grade_command(args: argparse.Namespace) -> int:
    tasks = {task["id"]: task for task in load_json(Path(args.tasks))["tasks"]}
    responses = load_json(Path(args.responses))["responses"]
    results = [
        grade_response(tasks[response["task_id"]], response)
        for response in responses
    ]

    output = format_markdown(results) if args.format == "markdown" else format_json(results)
    print(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Grade GIS/QGIS AI sample responses.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    grade = subparsers.add_parser("grade", help="Grade sample AI responses.")
    grade.add_argument("--tasks", required=True, help="Path to task_bank.json.")
    grade.add_argument("--responses", required=True, help="Path to sample_ai_responses.json.")
    grade.add_argument("--format", choices=["json", "markdown"], default="json")
    grade.set_defaults(func=grade_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
