from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _run_step(command: list[str], cwd: Path, env: dict[str, str], label: str) -> None:
	print(f"\n[{label}] Running: {' '.join(command)}")
	subprocess.run(command, cwd=str(cwd), env=env, check=True)


def _load_env_file(env_file: Path, env: dict[str, str]) -> None:
	"""Load KEY=VALUE pairs from a .env file into env when keys are missing."""
	if not env_file.exists():
		return

	for raw_line in env_file.read_text(encoding="utf-8").splitlines():
		line = raw_line.strip()
		if not line or line.startswith("#") or "=" not in line:
			continue

		key, value = line.split("=", 1)
		key = key.strip()
		value = value.strip().strip('"').strip("'")
		if key and key not in env:
			env[key] = value


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Run the full FOMC pipeline: preprocess -> summarize -> compare -> report."
	)
	parser.add_argument(
		"--raw-dir",
		type=Path,
		default=Path("data/raw"),
		help="Directory containing source PDFs.",
	)
	parser.add_argument(
		"--docs",
		type=Path,
		default=Path("data/json/docs.json"),
		help="Path for extracted raw-text docs JSON.",
	)
	parser.add_argument(
		"--summary-output",
		type=Path,
		default=Path("data/json/summary_comparison.json"),
		help="Path for nested summary/comparison JSON.",
	)
	parser.add_argument(
		"--report-output",
		type=Path,
		default=Path("output/fomc_report.md"),
		help="Path for final markdown report.",
	)
	parser.add_argument(
		"--model",
		type=str,
		default=None,
		help="OpenAI model for summarization/comparison (overrides OPENAI_MODEL).",
	)
	parser.add_argument(
		"--env-file",
		type=Path,
		default=Path(".env"),
		help="Optional .env file to load environment variables from.",
	)
	parser.add_argument(
		"--no-resume",
		action="store_true",
		help="Regenerate summaries/comparisons from scratch.",
	)
	parser.add_argument("--skip-preprocess", action="store_true", help="Skip PDF-to-JSON extraction step.")
	parser.add_argument("--skip-summarization", action="store_true", help="Skip summarization step.")
	parser.add_argument("--skip-comparison", action="store_true", help="Skip comparison step.")
	parser.add_argument("--skip-report", action="store_true", help="Skip report generation step.")
	args = parser.parse_args()

	repo_root = Path(__file__).resolve().parents[1]
	env = os.environ.copy()
	_load_env_file(repo_root / args.env_file, env)

	if args.model:
		env["OPENAI_MODEL"] = args.model

	needs_openai = not args.skip_summarization or not args.skip_comparison
	if needs_openai and not env.get("OPENAI_API_KEY"):
		raise EnvironmentError("OPENAI_API_KEY is not set. Set it before running summarization/comparison.")

	python = sys.executable

	if not args.skip_preprocess:
		_run_step(
			[
				python,
				"src/preprocessing/pdf_json.py",
				"--raw-dir",
				str(args.raw_dir),
				"--output",
				str(args.docs),
			],
			cwd=repo_root,
			env=env,
			label="Preprocess",
		)

	if not args.skip_summarization:
		summarization_cmd = [
			python,
			"src/genai/summarization.py",
			"--docs",
			str(args.docs),
			"--output",
			str(args.summary_output),
		]
		if args.no_resume:
			summarization_cmd.append("--no-resume")
		_run_step(summarization_cmd, cwd=repo_root, env=env, label="Summarization")

	if not args.skip_comparison:
		comparison_cmd = [
			python,
			"src/genai/comparison.py",
			"--summaries",
			str(args.summary_output),
			"--docs",
			str(args.docs),
			"--output",
			str(args.summary_output),
		]
		if args.no_resume:
			comparison_cmd.append("--no-resume")
		_run_step(comparison_cmd, cwd=repo_root, env=env, label="Comparison")

	if not args.skip_report:
		_run_step(
			[
				python,
				"-m",
				"src.postprocessing.generate_report",
				"--input",
				str(args.summary_output),
				"--output",
				str(args.report_output),
			],
			cwd=repo_root,
			env=env,
			label="Report",
		)

	print("\nPipeline completed successfully.")


if __name__ == "__main__":
	main()
