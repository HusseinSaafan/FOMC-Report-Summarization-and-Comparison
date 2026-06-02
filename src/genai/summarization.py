from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from openai import OpenAI

try:
	from src.genai.prompts import SUMMARIZATION_PROMPT, SYSTEM_PROMPT
except ModuleNotFoundError:
	# Allows running as: python src/genai/summarization.py
	from prompts import SUMMARIZATION_PROMPT, SYSTEM_PROMPT


def load_docs(docs_path: Path) -> dict[str, str]:
	with docs_path.open("r", encoding="utf-8") as file:
		data = json.load(file)

	if not isinstance(data, dict):
		raise ValueError(f"Expected a JSON object in {docs_path}, got {type(data).__name__}.")

	validated: dict[str, str] = {}
	for key, value in data.items():
		if not isinstance(key, str):
			continue
		validated[key] = value if isinstance(value, str) else str(value)

	return validated


def load_existing_summaries(output_path: Path) -> dict[str, str]:
	if not output_path.exists():
		return {}

	with output_path.open("r", encoding="utf-8") as file:
		content = file.read().strip()

	if not content:
		return {}

	try:
		data = json.loads(content)
	except json.JSONDecodeError:
		return {}

	if not isinstance(data, dict):
		return {}

	validated: dict[str, str] = {}
	for key, value in data.items():
		if isinstance(key, str) and isinstance(value, str):
			validated[key] = value

	return validated


def render_user_prompt(input_text: str) -> str:
	if "{input_text}" in SUMMARIZATION_PROMPT:
		return SUMMARIZATION_PROMPT.format(input_text=input_text)

	return f"{SUMMARIZATION_PROMPT}\n\n## INPUT\n{input_text}"


def summarize_text(client: OpenAI, model: str, input_text: str) -> str:
	user_prompt = render_user_prompt(input_text)
	response = client.responses.create(
		model=model,
		input=[
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": user_prompt},
		],
	)

	return response.output_text.strip()


def save_summaries(summaries: dict[str, str], output_path: Path) -> None:
	output_path.parent.mkdir(parents=True, exist_ok=True)
	tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
	with tmp_path.open("w", encoding="utf-8") as file:
		json.dump(summaries, file, ensure_ascii=False, indent=2)
	tmp_path.replace(output_path)


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Summarize each report in data/json/docs.json using OpenAI and write key-to-summary JSON output."
	)
	parser.add_argument(
		"--docs",
		type=Path,
		default=Path("data/json/docs.json"),
		help="Input docs JSON path (key -> raw text).",
	)
	parser.add_argument(
		"--output",
		type=Path,
		default=Path("data/json/summary_comparison.json"),
		help="Output summary JSON path (key -> summary).",
	)
	parser.add_argument(
		"--model",
		type=str,
		default=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
		help="OpenAI model to use. Defaults to OPENAI_MODEL or gpt-4.1-mini.",
	)
	parser.add_argument(
		"--no-resume",
		action="store_true",
		help="Do not resume from existing output file; start from an empty summary map.",
	)
	args = parser.parse_args()

	if not os.getenv("OPENAI_API_KEY"):
		raise EnvironmentError("OPENAI_API_KEY is not set.")

	docs = load_docs(args.docs)
	client = OpenAI()

	summaries: dict[str, str] = {} if args.no_resume else load_existing_summaries(args.output)
	if summaries:
		print(f"Loaded {len(summaries)} existing summaries from {args.output}")

	processed = 0
	failures = 0
	for key, value in docs.items():
		if key in summaries and summaries[key].strip():
			print(f"Skipping existing summary: {key}")
			continue

		if not value.strip():
			summaries[key] = ""
			save_summaries(summaries, args.output)
			processed += 1
			continue

		print(f"Summarizing: {key}")
		try:
			summaries[key] = summarize_text(client=client, model=args.model, input_text=value)
			processed += 1
		except Exception as error:
			failures += 1
			print(f"Failed: {key} ({type(error).__name__}: {error})")
			continue

		save_summaries(summaries, args.output)

	save_summaries(summaries, args.output)
	print(
		f"Wrote {len(summaries)} summaries to {args.output} "
		f"(processed={processed}, failures={failures})"
	)


if __name__ == "__main__":
	main()
