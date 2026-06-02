from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from openai import OpenAI

try:
	from src.genai.prompts import COMPARISON_PROMPT, SYSTEM_PROMPT
except ModuleNotFoundError:
	from prompts import COMPARISON_PROMPT, SYSTEM_PROMPT

# Canonical month ordering used to sort report keys chronologically.
_MONTH_ORDER: dict[str, int] = {
	"jan": 1, "feb": 2, "mar": 3, "apr": 4,
	"may": 5, "jun": 6, "jul": 7, "aug": 8,
	"sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _month_rank(key: str) -> int:
	"""Return sort rank for a month key; unknown keys sort to the end."""
	return _MONTH_ORDER.get(key.lower(), 999)


def load_summaries(path: Path) -> dict[str, str]:
	"""Load key -> summarization text from the nested summary_comparison.json format."""
	content = path.read_text(encoding="utf-8").strip()
	if not content:
		raise ValueError(f"{path} is empty.")
	data = json.loads(content)
	if not isinstance(data, dict):
		raise ValueError(f"Expected a JSON object in {path}.")
	result: dict[str, str] = {}
	for k, v in data.items():
		if not isinstance(k, str):
			continue
		if isinstance(v, dict):
			text = v.get("summarization", "")
			result[k] = text if isinstance(text, str) else ""
		elif isinstance(v, str):
			result[k] = v
	return result


def load_existing_output(path: Path) -> dict[str, dict]:
	"""Load existing docs.json if present; tolerates missing or malformed file."""
	if not path.exists():
		return {}
	content = path.read_text(encoding="utf-8").strip()
	if not content:
		return {}
	try:
		data = json.loads(content)
	except json.JSONDecodeError:
		return {}
	if not isinstance(data, dict):
		return {}
	return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, dict)}


def render_comparison_prompt(previous_summary: str, current_summary: str) -> str:
	input_text = (
		f"### PREVIOUS REPORT SUMMARY\n{previous_summary}\n\n"
		f"### CURRENT REPORT SUMMARY\n{current_summary}"
	)
	if "{input_text}" in COMPARISON_PROMPT:
		return COMPARISON_PROMPT.format(input_text=input_text)
	return f"{COMPARISON_PROMPT}\n\n## INPUT\n{input_text}"


def compare_summaries(client: OpenAI, model: str, previous: str, current: str) -> str:
	user_prompt = render_comparison_prompt(previous, current)
	response = client.responses.create(
		model=model,
		input=[
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": user_prompt},
		],
	)
	return response.output_text.strip()


def save_output(data: dict[str, dict], path: Path) -> None:
	"""Write output in chronological order starting from jan."""
	path.parent.mkdir(parents=True, exist_ok=True)
	ordered = dict(sorted(data.items(), key=lambda kv: _MONTH_ORDER.get(kv[0].lower(), 999)))
	tmp = path.with_suffix(path.suffix + ".tmp")
	with tmp.open("w", encoding="utf-8") as f:
		json.dump(ordered, f, ensure_ascii=False, indent=2)
	tmp.replace(path)


def main() -> None:
	parser = argparse.ArgumentParser(
		description=(
			"Compare consecutive FOMC summaries using an LLM and write enriched "
			"output to data/json/docs.json."
		)
	)
	parser.add_argument(
		"--summaries",
		type=Path,
		default=Path("data/json/summary_comparison.json"),
		help="Input JSON path (key -> summary string).",
	)
	parser.add_argument(
		"--output",
		type=Path,
		default=Path("data/json/summary_comparison.json"),
		help="Output JSON path (key -> {summarization, comparison}).",
	)
	parser.add_argument(
		"--model",
		type=str,
		default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
		help="OpenAI model to use. Defaults to OPENAI_MODEL env var or gpt-4o-mini.",
	)
	parser.add_argument(
		"--no-resume",
		action="store_true",
		help="Ignore existing output and regenerate all comparisons.",
	)
	args = parser.parse_args()

	if not os.getenv("OPENAI_API_KEY"):
		raise EnvironmentError("OPENAI_API_KEY is not set.")

	summaries = load_summaries(args.summaries)

	# Sort keys into chronological order.
	ordered_keys = sorted(summaries.keys(), key=_month_rank)
	print(f"Processing {len(ordered_keys)} reports in order: {ordered_keys}")

	output: dict[str, dict] = {} if args.no_resume else load_existing_output(args.output)
	client = OpenAI()

	processed = 0
	failures = 0

	for i, key in enumerate(ordered_keys):
		current_summary = summaries[key]

		# Resume: skip if comparison already generated.
		if key in output and output[key].get("comparison", "").strip():
			print(f"Skipping (already done): {key}")
			continue

		# First month has no previous report to compare against.
		if i == 0:
			output[key] = {"summarization": current_summary, "comparison": ""}
			print(f"First report, no comparison: {key}")
			save_output(output, args.output)
			processed += 1
			continue

		prev_key = ordered_keys[i - 1]
		previous_summary = summaries.get(prev_key, "")

		if not previous_summary.strip() or not current_summary.strip():
			output[key] = {"summarization": current_summary, "comparison": ""}
			print(f"Skipping comparison (empty summary): {key}")
			save_output(output, args.output)
			processed += 1
			continue

		print(f"Comparing: {prev_key} -> {key}")
		try:
			comparison = compare_summaries(
				client=client,
				model=args.model,
				previous=previous_summary,
				current=current_summary,
			)
			output[key] = {"summarization": current_summary, "comparison": comparison}
			processed += 1
		except Exception as error:
			failures += 1
			print(f"Failed: {key} ({type(error).__name__}: {error})")
			# Preserve existing summarization even if comparison fails.
			if key not in output:
				output[key] = {"summarization": current_summary, "comparison": ""}
			continue

		save_output(output, args.output)

	save_output(output, args.output)
	print(
		f"Done. Wrote {len(output)} entries to {args.output} "
		f"(processed={processed}, failures={failures})"
	)


if __name__ == "__main__":
	main()
