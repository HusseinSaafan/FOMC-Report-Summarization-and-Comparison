SYSTEM_PROMPT = """
You are an expert macro-financial research assistant focused on Federal Reserve communication.
"""

SUMMARIZATION_PROMPT = """
## OBJECTIVE
Summarize the FOMC report into a concise, decision-useful markdown brief while preserving core financial and macroeconomic information.

## RULES
1. Preserve substance over style: do not omit materially relevant policy, inflation, labor, growth, or financial-conditions details.
2. Do not fabricate numbers, dates, or claims. If uncertain or not stated, write "Not specified in the report.".
3. Keep central bank language faithful: distinguish between facts, guidance, risks, and uncertainty.
4. Capture directional signals explicitly (rising/falling/stable, tightening/easing, upside/downside risk).
5. Include all explicit policy actions and forward guidance (rates, balance sheet, voting, dissent if present).
6. Reflect market-relevant implications for rates, inflation expectations, growth outlook, employment, and risk sentiment.
7. Prefer concrete details (percentages, basis points, time references) when present in the source.
8. Avoid generic commentary and avoid repeating the same point in multiple sections.

## FORMATTING INSTRUCTIONS
1. Output must be valid markdown only.
2. Output must be a single markdown string, not JSON and not a Python dictionary.
3. Use the exact section headers below and keep this order:
	- # FOMC Summary
	- ## Policy Decision
	- ## Economic Conditions
	- ## Inflation and Prices
	- ## Labor Market
	- ## Financial Conditions and Markets
	- ## Risks and Uncertainty
	- ## Forward Guidance and Policy Path
	- ## Analyst Takeaways
4. In each section, use 3-6 bullet points.
5. Keep each bullet to one sentence when possible.
6. End with a short "Analyst Takeaways" section containing:
	- 2 bullish signals
	- 2 bearish signals
	- 2 indicators to monitor next
7. Keep the total output between 220 and 320 words.
8. In sections other than "Analyst Takeaways", use exactly 3 bullets per section.
9. Cap each bullet at 16 words and avoid subordinate clauses unless required for precision.
10. Prioritize only first-order policy and macro signals; drop low-materiality detail.

## EXAMPLE
# FOMC Summary
## Policy Decision
- The Committee held the target range unchanged at 5.25%-5.50%, signaling a data-dependent stance.
- Balance sheet runoff continued at the previously announced pace.

## Economic Conditions
- Real activity expanded at a moderate pace, with consumption resilient but business investment mixed.
- Housing activity remained constrained by elevated financing costs.

## Inflation and Prices
- Inflation eased from prior peaks but remained above target, with core services showing persistence.
- Committee communication emphasized continued progress is needed before easing.

## Labor Market
- Payroll growth moderated but remained positive, while unemployment stayed low.
- Wage growth softened gradually yet remained above pre-pandemic norms.

## Financial Conditions and Markets
- Treasury yields were volatile around policy expectations, while credit spreads stayed relatively contained.
- Broader financial conditions remained restrictive compared with long-run averages.

## Risks and Uncertainty
- Upside inflation risk persisted due to sticky services prices.
- Downside growth risk rose from tighter credit transmission.

## Forward Guidance and Policy Path
- The Committee reiterated dependence on incoming data, the evolving outlook, and balance of risks.
- Near-term bias remained cautious, with no preset path for cuts.

## Analyst Takeaways
- Bullish: Disinflation trend continued in goods categories.
- Bullish: Labor market rebalanced without sharp deterioration.
- Bearish: Core services inflation remained sticky.
- Bearish: Restrictive financial conditions could pressure growth-sensitive sectors.
- Monitor next: Core PCE and wage growth momentum.
- Monitor next: Credit conditions and unemployment claims.

## INPUT
{input_text}
"""
### each section should be written in the following format:
### section title:


COMPARISON_PROMPT = """
## OBJECTIVE
Compare two FOMC report summaries and produce a concise, decision-useful markdown brief that highlights what changed, why it matters, and the likely market interpretation.

## RULES
1. Compare content faithfully: do not invent policy actions, macro trends, votes, or market reactions not present in the inputs.
2. Distinguish clearly between:
	- New information in the current report
	- Information removed or softened versus the previous report
	- Information that is unchanged
3. Capture directional shifts explicitly (more hawkish/dovish, tighter/easier, stronger/weaker growth, higher/lower inflation risk).
4. Prioritize economically material differences: policy rate stance, forward guidance, inflation narrative, labor assessment, balance sheet language, risk balance, and dissent.
5. When data points, dates, basis points, or vote counts are available, include them exactly.
6. If a requested element is missing in either input, write "Not specified in the provided summaries.".
7. Keep central bank language precise and avoid overinterpreting ambiguous wording.
8. Avoid repetition and generic filler; every bullet should convey a distinct comparison insight.

## FORMATTING INSTRUCTIONS
1. Output must be valid markdown only.
2. Output must be a single markdown string, not JSON and not a Python dictionary.
3. Use the exact section headers below and keep this order:
	- # FOMC Comparison
	- ## Executive Shift
	- ## Policy Decision Delta
	- ## Economic Conditions Delta
	- ## Inflation and Prices Delta
	- ## Labor Market Delta
	- ## Financial Conditions and Markets Delta
	- ## Risks and Uncertainty Delta
	- ## Forward Guidance Delta
	- ## Market and Strategy Implications
	- ## Bottom Line
4. In each section, use 3-6 bullet points, except:
	- ## Executive Shift: exactly 3 bullets
	- ## Bottom Line: exactly 3 bullets
5. Keep each bullet to one sentence when possible.
6. In every delta section, label bullets with one of these prefixes:
	- Increased:
	- Decreased:
	- Unchanged:
7. In "Market and Strategy Implications", include impacts for:
	- Rates
	- Inflation expectations
	- Growth risk sentiment
	- Labor sensitivity
8. Keep the total output between 240 and 340 words.
9. Use exactly 3 bullets in every section.
10. Cap each bullet at 16 words; keep only the most decision-relevant deltas.
11. If multiple similar changes exist, aggregate into one bullet instead of listing each instance.

## EXAMPLE
# FOMC Comparison
## Executive Shift
- The statement tone shifted modestly dovish as inflation progress received greater emphasis than in the previous report.
- Forward guidance remained data dependent, but language reduced urgency around additional tightening.
- The risk balance moved toward two-sided concerns rather than primarily inflation upside.

## Policy Decision Delta
- Unchanged: The target range was held constant in both reports.
- Decreased: The current report softened language about the need for further policy restraint.
- Increased: Communication around optionality for future adjustments became more explicit.

## Economic Conditions Delta
- Increased: The current report described activity as more resilient than previously characterized.
- Unchanged: Consumption was still noted as supportive of aggregate demand.
- Decreased: References to sectoral weakness were less prominent than in the prior report.

## Inflation and Prices Delta
- Decreased: The current report placed more weight on disinflation progress than the previous one.
- Unchanged: Inflation remained above target in both summaries.
- Increased: Confidence in medium-term inflation normalization was described as stronger.

## Labor Market Delta
- Unchanged: Employment conditions were still characterized as broadly solid.
- Decreased: Concern about overheating in wages was less explicit than before.
- Increased: Signs of labor market rebalancing were emphasized more clearly.

## Financial Conditions and Markets Delta
- Decreased: The current report implied slightly less restrictive financial conditions.
- Unchanged: Market volatility around policy expectations remained a relevant theme.
- Increased: Sensitivity of rate pricing to incoming inflation data was highlighted more strongly.

## Risks and Uncertainty Delta
- Decreased: Upside inflation risk language was less forceful than in the previous report.
- Increased: Downside growth risk received relatively more attention.
- Unchanged: Policy uncertainty remained elevated and data dependence remained central.

## Forward Guidance Delta
- Unchanged: The Committee maintained no preset path and emphasized incoming data.
- Decreased: The probability implied for further tightening language declined.
- Increased: Optionality around eventual easing was indirectly acknowledged.

## Market and Strategy Implications
- Rates: The language shift supports a lower near-term probability of further hikes versus the prior report.
- Inflation expectations: Improved confidence in disinflation may reduce upside repricing risk.
- Growth risk sentiment: Greater attention to downside growth risk can support defensive positioning.
- Labor sensitivity: Incoming employment data should carry higher marginal signal for policy timing.

## Bottom Line
- The net communication shift is mildly dovish relative to the previous report.
- Policy remains restrictive, but the threshold for additional tightening appears higher.
- Next reports should be monitored for confirmation in core inflation and labor rebalancing signals.

## INPUT
{input_text}
"""