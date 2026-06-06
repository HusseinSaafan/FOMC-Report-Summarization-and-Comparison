from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from openai import OpenAI

try:
	from src.genai.prompts import SUMMARIZATION_PROMPT, SYSTEM_PROMPT
except ModuleNotFoundError:
	# Allows running as: python src/genai/summarization.py
	from prompts import SUMMARIZATION_PROMPT, SYSTEM_PROMPT

_MONTH_ORDER: dict[str, int] = {
	"jan": 1, "feb": 2, "mar": 3, "apr": 4,
	"may": 5, "jun": 6, "jul": 7, "aug": 8,
	"sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

_UNSUPPORTED_TERMS: tuple[str, ...] = (
	"wage",
	"credit spread",
	"market volatility",
	"financial stability",
	"long-term average",
)


def _normalize_doc_key(key: str) -> str:
	base = key.strip().lower().replace(".pdf", "")
	if base in _MONTH_ORDER:
		return base
	if len(base) >= 3 and base[:3] in _MONTH_ORDER:
		return base[:3]
	return base


def load_docs(docs_path: Path) -> dict[str, str]:
	with docs_path.open("r", encoding="utf-8") as file:
		data = json.load(file)

	if not isinstance(data, dict):
		raise ValueError(f"Expected a JSON object in {docs_path}, got {type(data).__name__}.")

	validated: dict[str, str] = {}
	for key, value in data.items():
		if not isinstance(key, str):
			continue
		normalized_key = _normalize_doc_key(key)
		if isinstance(value, str):
			validated[normalized_key] = value
		elif isinstance(value, dict):
			# Backward compatibility if docs.json accidentally stores generated objects.
			fallback = value.get("text") or value.get("raw") or value.get("summarization") or ""
			validated[normalized_key] = fallback if isinstance(fallback, str) else str(fallback)
		else:
			validated[normalized_key] = str(value)

	return validated


def load_existing_summaries(output_path: Path) -> dict[str, str]:
	"""Load existing summarization texts from the nested output format."""
	if not output_path.exists():
		return {}

	content = output_path.read_text(encoding="utf-8").strip()
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
		if not isinstance(key, str):
			continue
		normalized_key = _normalize_doc_key(key)
		if isinstance(value, dict):
			# New nested format: {key: {"summarization": "...", "comparison": "..."}}
			text = value.get("summarization", "")
			validated[normalized_key] = text if isinstance(text, str) else ""
		elif isinstance(value, str):
			validated[normalized_key] = value

	return validated


def render_user_prompt(input_text: str) -> str:
	if "{input_text}" in SUMMARIZATION_PROMPT:
		return SUMMARIZATION_PROMPT.format(input_text=input_text)

	return f"{SUMMARIZATION_PROMPT}\n\n## INPUT\n{input_text}"


def _drop_unsupported_claims(text: str, source_text: str) -> str:
	"""Drop sentences that mention unsupported market/wage claims absent in source."""
	source_lower = source_text.lower()
	chunks = text.splitlines()
	out_lines: list[str] = []
	for line in chunks:
		if line.startswith("#") or not line.strip():
			out_lines.append(line)
			continue
		parts = re.split(r"(?<=[.!?])\s+", line)
		kept: list[str] = []
		for sentence in parts:
			s = sentence.strip()
			if not s:
				continue
			if any(term in s.lower() and term not in source_lower for term in _UNSUPPORTED_TERMS):
				continue
			kept.append(s)
		if kept:
			out_lines.append(" ".join(kept))
	return "\n".join(out_lines).strip()


def _normalize_markdown(text: str, max_words: int = 130) -> str:
	"""Apply light normalization and cap output length for concise summaries."""
	lines = [line.rstrip() for line in text.splitlines()]

	# Keep markdown structure but avoid extra vertical space.
	normalized: list[str] = []
	blank_streak = 0
	for line in lines:
		if not line.strip():
			blank_streak += 1
			if blank_streak > 1:
				continue
		else:
			blank_streak = 0
		normalized.append(line)

	joined = "\n".join(normalized).strip()
	if not joined:
		return joined

	words = joined.split()
	if len(words) <= max_words:
		return joined

	# Truncate by lines to preserve markdown headings and section breaks.
	result_lines: list[str] = []
	used = 0
	for line in joined.splitlines():
		parts = line.split()
		if not parts:
			result_lines.append("")
			continue
		remaining = max_words - used
		if remaining <= 0:
			break
		if len(parts) <= remaining:
			result_lines.append(line)
			used += len(parts)
			continue

		result_lines.append(" ".join(parts[:remaining]).rstrip(" .,;:") + "...")
		used = max_words
		break

	return "\n".join(result_lines).strip()


def summarize_text(client: OpenAI, model: str, input_text: str) -> str:
	user_prompt = render_user_prompt(input_text)
	response = client.responses.create(
		model=model,
		input=[
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": user_prompt},
		],
	)

	filtered = _drop_unsupported_claims(response.output_text.strip(), input_text)
	return _normalize_markdown(filtered, max_words=130)


def save_summaries(summaries: dict[str, str], output_path: Path) -> None:
	"""Write summarizations in nested format, ordered chronologically from jan."""
	output_path.parent.mkdir(parents=True, exist_ok=True)
	ordered_keys = sorted(summaries.keys(), key=lambda k: _MONTH_ORDER.get(k.lower(), 999))
	output = {key: {"summarization": summaries[key], "comparison": ""} for key in ordered_keys}
	tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
	with tmp_path.open("w", encoding="utf-8") as file:
		json.dump(output, file, ensure_ascii=False, indent=2)
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
		default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
		help="OpenAI model to use. Defaults to OPENAI_MODEL or gpt-4o-mini.",
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
