# FOMC Report Summarization and Comparison

This project builds a month-by-month FOMC analysis pipeline.

It takes raw FOMC statement PDFs, extracts text, generates grounded summaries, compares each month with the prior month, and writes a final markdown report.

## What the pipeline does

1. Preprocessing: extracts statement text from PDF files in data/raw.
2. Summarization: generates concise monthly summaries from raw statement text.
3. Comparison: compares each month to the previous month using raw statements as evidence.
4. Report generation: creates a single markdown report in output/fomc_report.md.

## Project structure

- data/raw: input FOMC statement PDFs.
- data/json/docs.json: extracted raw statement text.
- data/json/summary_comparison.json: structured model output with summarization and comparison.
- output/fomc_report.md: final report.
- src/preprocessing/pdf_json.py: PDF text extraction.
- src/genai/summarization.py: monthly summarization.
- src/genai/comparison.py: month-to-month comparison.
- src/postprocessing/generate_report.py: markdown report builder.
- src/main.py: full pipeline runner.

## Requirements

- Python 3.9+
- OpenAI API key

Python dependencies are listed in requirements.txt.

## Installation

1. Create and activate a virtual environment.
2. Install dependencies.

Example commands:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Configuration

Set your OpenAI API key as an environment variable.

Option A: export in shell

export OPENAI_API_KEY=your_key_here

Option B: create a .env file in repository root

OPENAI_API_KEY=your_key_here

You can also optionally set:

OPENAI_MODEL=gpt-4o-mini

## Run the full pipeline

Run everything end to end:

python -m src.main --model gpt-4o-mini

Force full regeneration:

python -m src.main --model gpt-4o-mini --no-resume

## Useful runner options

- --skip-preprocess: skip PDF extraction.
- --skip-summarization: skip monthly summarization.
- --skip-comparison: skip month comparisons.
- --skip-report: skip markdown report generation.
- --raw-dir: set custom PDF input directory.
- --docs: set custom docs JSON path.
- --summary-output: set custom summary/comparison JSON path.
- --report-output: set custom final report path.
- --env-file: set custom env file path.

Show help:

python -m src.main --help

## Outputs

After a successful run, these files are produced or updated:

- data/json/docs.json
- data/json/summary_comparison.json
- output/fomc_report.md

## Notes on accuracy controls

The generation prompts and post-filters are tuned to reduce unsupported claims.

The comparison stage uses raw statements as evidence to reduce summary-to-summary drift.

## License

Add your preferred license in a LICENSE file.
