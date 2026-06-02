from __future__ import annotations

import argparse
import json
from pathlib import Path

from pypdf import PdfReader


def extract_pdf_text(pdf_path: Path) -> str:
	"""Extract all text from a PDF file, preserving page order."""
	reader = PdfReader(str(pdf_path))
	pages_text: list[str] = []

	for page in reader.pages:
		page_text = page.extract_text() or ""
		pages_text.append(page_text)

	return "\n".join(pages_text).strip()


def build_docs_map(raw_dir: Path) -> dict[str, str]:
	"""Return a mapping of PDF filename to extracted text content."""
	docs: dict[str, str] = {}

	for pdf_path in sorted(raw_dir.glob("*.pdf")):
		docs[pdf_path.name] = extract_pdf_text(pdf_path)

	return docs


def save_docs_json(docs: dict[str, str], output_path: Path) -> None:
	"""Persist extracted documents as pretty-printed JSON."""
	output_path.parent.mkdir(parents=True, exist_ok=True)
	tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
	with tmp_path.open("w", encoding="utf-8") as file:
		json.dump(docs, file, ensure_ascii=False, indent=2)
	# Atomic replace avoids leaving an empty/truncated target file on interruption.
	tmp_path.replace(output_path)


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Extract all PDF text from data/raw into data/json/docs.json"
	)
	parser.add_argument(
		"--raw-dir",
		type=Path,
		default=Path("data/raw"),
		help="Directory containing input PDF files.",
	)
	parser.add_argument(
		"--output",
		type=Path,
		default=Path("data/json/docs.json"),
		help="Output JSON path.",
	)
	args = parser.parse_args()

	docs = build_docs_map(args.raw_dir)
	save_docs_json(docs, args.output)
	print(f"Wrote {len(docs)} documents to {args.output}")


if __name__ == "__main__":
	main()
