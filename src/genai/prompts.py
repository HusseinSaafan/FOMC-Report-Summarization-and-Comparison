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
