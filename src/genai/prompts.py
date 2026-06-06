SYSTEM_PROMPT = """
You are an expert macro-financial research assistant focused on Federal Reserve communication.
"""

SUMMARIZATION_PROMPT = """
## OBJECTIVE
Summarize the FOMC statement into a brief, accurate note that is strictly grounded in the provided text.

## RULES
1. Use only information explicitly present in the statement; do not invent facts, numbers, tone shifts, or market effects.
2. Prioritize: policy action, vote split/dissents, balance-sheet operations, inflation language, labor language, growth language, and risk language.
3. If dissent exists, include who dissented and what alternative action they preferred.
4. If operations language exists (runoff caps, concluding runoff, reserve-management purchases), include it briefly.
5. Do not mention wage growth, credit spreads, market volatility, or financial-conditions assessments unless those terms are explicitly in the statement.
6. Avoid stronger wording than the statement (e.g., do not upgrade "attentive" into "heightened vigilance" unless stated).
7. Keep interpretation restrained and separate from factual recap.

## FORMATTING INSTRUCTIONS
1. Output must be valid markdown only.
2. Output must be a single markdown string, not JSON and not a Python dictionary.
3. Use exactly this structure:
	- # FOMC Summary
	- ## Snapshot
	- ## Why It Matters
4. Write in paragraph style, not bullet points.
5. "Snapshot" must be 55-85 words.
6. "Why It Matters" must be 25-45 words.
7. Total length must be 85-130 words.
8. Do not use phrases like "No change" or "Not specified" unless essential for clarity.
9. Do not repeat the same idea across both sections.
10. Prefer near-paraphrase of key official wording over creative rewriting.

## EXAMPLE
# FOMC Summary
## Snapshot
The Committee kept policy restrictive while signaling a continued data-dependent stance. Inflation progress was acknowledged but not declared complete, with attention still on core pressures. Activity remained resilient overall, though uneven across sectors. Labor conditions were described as solid but gradually cooling. Risk language stayed balanced, with inflation persistence and growth slowing both relevant to the outlook.

## Why It Matters
The message supports a cautious path: no immediate policy pivot, but less urgency for additional tightening unless inflation re-accelerates. Markets should focus on incoming inflation and labor data as the main triggers for any shift in policy timing.

## INPUT
{input_text}
"""

COMPARISON_PROMPT = """
## OBJECTIVE
Compare two FOMC statements and produce a very brief, evidence-grounded delta note that highlights only meaningful changes.

## RULES
1. Compare faithfully; do not invent changes, rationale, or market effects.
2. Use only differences that are explicit in the two statements.
3. Prioritize deltas in: policy rate action, dissents/vote split, balance-sheet operations, inflation wording, labor wording, growth wording, and risk wording.
4. If there is no explicit meaningful change in a category, omit that category entirely.
5. Never add filler lines that only say unchanged/no change.
6. Do not claim "progress" or "intensification" unless the statement language directly supports it.
7. Keep interpretation restrained and tied to explicit textual differences.
8. Ignore routine participant roster or alternate-member changes unless they are directly tied to a recorded dissent.

## FORMATTING INSTRUCTIONS
1. Output must be valid markdown only.
2. Output must be a single markdown string, not JSON and not a Python dictionary.
3. Use exactly this structure:
	- # FOMC Comparison
	- ## Key Deltas
	- ## Net Interpretation
4. Write in paragraph style, not bullet points.
5. "Key Deltas" must be 40-70 words and include only 1-3 meaningful changes.
6. "Net Interpretation" must be 20-35 words with the overall hawkish/dovish/neutral read.
7. Total length must be 65-105 words.
8. If almost nothing changed, state that once in one sentence and stop.
9. Avoid boilerplate and avoid repeating points between sections.
10. Mention dissent and balance-sheet operational changes when they are material.

## EXAMPLE
# FOMC Comparison
## Key Deltas
Compared with the prior report, the current communication places slightly more emphasis on disinflation progress and slightly less emphasis on additional tightening. Growth language remains constructive but with greater acknowledgement of downside sensitivity, while labor commentary points to gradual cooling rather than renewed overheating. Forward guidance stays data dependent, but the tone suggests somewhat higher tolerance for waiting before any further policy adjustment.

## Net Interpretation
The overall shift reads mildly dovish in tone, not a regime change. Policy remains restrictive, but the reaction function appears less asymmetric toward further tightening unless inflation momentum worsens.

## INPUT
{input_text}
"""