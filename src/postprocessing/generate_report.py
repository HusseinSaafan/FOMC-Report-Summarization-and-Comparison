"""
Generate a single Markdown report from data/json/summary_comparison.json.

Each month gets two sections:
  - Summary   (the summarization text)
  - Comparison to previous month (the comparison text, or a note for the first month)

Usage:
    python -m src.postprocessing.generate_report
    python -m src.postprocessing.generate_report --input data/json/summary_comparison.json --output output/fomc_report.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

_MONTH_ORDER: dict[str, int] = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

_MONTH_LABEL: dict[str, str] = {
    "jan": "January", "feb": "February", "mar": "March", "apr": "April",
    "may": "May", "jun": "June", "jul": "July", "aug": "August",
    "sep": "September", "oct": "October", "nov": "November", "dec": "December",
}


def load_data(input_path: Path) -> dict[str, dict]:
    content = input_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"{input_path} is empty.")
    return json.loads(content)


def build_report(data: dict[str, dict]) -> str:
    ordered_keys = sorted(data.keys(), key=lambda k: _MONTH_ORDER.get(k.lower(), 999))

    lines: list[str] = [
        "# FOMC Reports Brief",
        "",
    ]

    for i, key in enumerate(ordered_keys):
        label = _MONTH_LABEL.get(key.lower(), key.upper())
        entry = data[key]

        summarization = (entry.get("summarization") or "").strip()
        comparison = (entry.get("comparison") or "").strip()

        lines.append(f"## {label}")
        lines.append("")

        # --- Summarization section ---
        lines.append("### Summary")
        lines.append("")
        if summarization:
            # Strip a leading "# FOMC Summary" heading that the LLM may have added
            summary_body = _strip_top_heading(summarization)
            lines.append(summary_body)
        else:
            lines.append("_No summary available._")
        lines.append("")

        # --- Comparison section ---
        lines.append("### Comparison to Previous Month")
        lines.append("")
        if comparison:
            comparison_body = _strip_top_heading(comparison)
            lines.append(comparison_body)
        elif i == 0:
            lines.append("_This is the first report in the series — no prior month to compare against._")
        else:
            prev_label = _MONTH_LABEL.get(ordered_keys[i - 1].lower(), ordered_keys[i - 1].upper())
            lines.append(f"_No comparison available for {label} vs {prev_label}._")
        lines.append("")

    return "\n".join(lines)


def _strip_top_heading(text: str) -> str:
    """Remove the first H1 line if the LLM included a redundant title heading."""
    first_line, _, rest = text.partition("\n")
    if first_line.startswith("# "):
        return rest.lstrip("\n")
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Markdown report from summary_comparison.json.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/json/summary_comparison.json"),
        help="Path to the input JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/fomc_report.md"),
        help="Path for the generated Markdown report.",
    )
    args = parser.parse_args()

    data = load_data(args.input)
    report = build_report(data)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Report written to {args.output}  ({len(data)} months)")


if __name__ == "__main__":
    main()
