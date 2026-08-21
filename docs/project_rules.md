# Stockball Stock — Research Rules

## Purpose

This document defines the rules governing all Stockball Stock research.

The goal is simple:

> **Make it harder for us to fool ourselves.**

A profitable-looking backtest is worthless if it was produced through biased data, accidental future knowledge, overfitting, unrealistic execution, or repeated modification until something worked.

These rules take priority over producing impressive results.

---

# 1. Every Experiment Starts With a Hypothesis

Before running an experiment, document:

* Experiment ID
* Research question
* Hypothesis
* Assets being tested
* Historical period
* Input variables
* Exact signal conditions
* Holding periods
* Benchmark/control
* Primary measurements
* Known limitations

Only then may the experiment be run.

---

# 2. Experiments Are Immutable

Once an experiment produces results, its specification is frozen.

Do not change:

* thresholds
* indicators
* assets
* dates
* holding periods
* filters
* calculations

because the result was disappointing.

A modification becomes a new experiment.

> **Result → Question → New Experiment**

Never:

> **Result → Tweak → Better Result → Rewrite History**

---

# 3. Preserve Every Result

Successful, unsuccessful, boring, and inconclusive experiments must all remain in the Experiment Registry.

We do not delete failed experiments.

Failed experiments tell us where an edge probably does **not** exist and help prevent us from unknowingly repeating the same research.

---

# 4. No Future Information

A decision occurring on date **T** may only use information that would genuinely have been available on or before date **T**.

Future information must never leak into a historical signal.

This includes:

* future prices
* future index membership
* revised economic data
* later financial statements
* future analyst estimates
* future corporate classifications

This is the **look-ahead rule**.

Violation invalidates the experiment.

---

# 5. Respect Publication Timing

Knowing when information occurred is not enough.

We must know when a historical investor could actually have known it.

For example:

A company's quarterly earnings may describe a quarter ending March 31 but may not have been published until May.

The information cannot be used for an April signal.

Where publication timing cannot be established reliably, the variable should either be excluded or explicitly marked as uncertain.

---

# 6. Avoid Survivorship Bias

Today's successful ETFs, companies, sectors, or indices must not automatically represent the historical investment universe.

Assets can:

* close
* merge
* delist
* fail
* change names
* change sectors
* leave indices

Whenever possible, research should include securities that existed at the historical time being studied.

If survivorship-free data is unavailable, the experiment must state this limitation.

---

# 7. Respect ETF Inception Dates

An ETF cannot generate observations before it existed.

Our target research period may span approximately 28 years, but each ETF begins contributing observations only when reliable historical data becomes available.

Never fabricate earlier ETF history simply to create an equal dataset.

Synthetic or proxy histories may eventually be researched, but they must be explicitly identified as such.

---

# 8. Raw Data Is Sacred

Original downloaded market data should be stored separately from processed data.

Structure:

`Raw Data → Processed Data → Experiment Dataset → Results`

Raw data should never be manually edited to improve an experiment.

Corrections should occur through documented processing code so they can be reproduced.

---

# 9. Data Sources Must Be Recorded

Every dataset must record, where practical:

* provider
* download/retrieval date
* ticker
* date range
* frequency
* adjusted/unadjusted status
* known missing periods
* transformations performed

If the underlying data changes, we should be able to identify which experiments used which version.

---

# 10. Corporate Actions Must Be Handled Correctly

Returns must account appropriately for events such as:

* stock splits
* ETF splits
* dividends
* distributions
* mergers
* ticker changes

For return research, adjusted prices or equivalent total-return calculations should normally be used where appropriate.

The exact methodology must remain consistent and documented.

---

# 11. Missing Data Is Not Zero

Missing observations must never automatically become:

`0`

Missing means:

`Unknown`

The system must explicitly decide whether to:

* exclude the observation
* forward-fill where methodologically justified
* obtain replacement data
* mark the experiment as incomplete

Missing data must never silently become favorable data.

---

# 12. Define the Signal Before the Outcome

Signal construction and outcome measurement must remain separate.

Example:

**Signal**

`SPY > 200DMA`

AND

`ETF 20-day return > 5%`

**Outcome**

`ETF return during the following 5 trading days`

Future outcomes may never participate in defining the signal that supposedly predicted them.

---

# 13. Compare Against a Baseline

A pattern is not useful merely because it produces positive returns.

Markets often rise.

Every experiment should therefore compare the pattern against an appropriate baseline.

Depending on the experiment, comparisons may include:

* unconditional ETF returns
* SPY
* sector benchmark
* random historical periods
* signal A alone
* signal B alone
* combined A + B

The relevant question is:

> **Did the pattern add information?**

Not simply:

> **Did prices rise afterward?**

---

# 14. Signal Stacking Must Earn Its Complexity

Adding another condition must demonstrate measurable improvement.

For example:

`Momentum`

vs.

`Momentum + Market Regime`

vs.

`Momentum + Market Regime + Sector Strength`

If another variable does not meaningfully improve probability, downside protection, robustness, or another predefined objective, complexity should not automatically be retained.

More indicators do not necessarily mean more intelligence.

---

# 15. Prefer Simple Explanations

When two models produce similar results, prefer the simpler model.

A pattern involving four understandable variables that survives many market regimes is generally more interesting than a pattern involving 27 precisely tuned parameters.

Complexity creates more opportunities for accidental fitting.

---

# 16. Thresholds Must Not Be Mined Carelessly

If an experiment tests:

`20-day return > 5%`

we cannot simply try:

`4.9%, 5.0%, 5.1%, 5.2% ...`

until we discover the most profitable historical number and then pretend that threshold was predetermined.

Threshold optimization is allowed only as an explicitly documented research experiment.

The number of alternatives tested must be recorded.

---

# 17. Beware Multiple Testing

If we test thousands of patterns, some will appear extraordinary purely by chance.

Therefore:

> **Discovery is not validation.**

The more hypotheses we test, the more skeptical we must become of unusually strong results.

Promising discoveries must survive additional testing before they are considered evidence of an edge.

---

# 18. Separate Discovery From Validation

Where sufficient data exists, research should eventually separate history into:

### Discovery Period

Used to discover and develop the pattern.

### Validation Period

Kept unseen while developing the hypothesis.

A pattern that works beautifully in discovery but fails validation should be treated as suspect.

Validation data must not become another optimization playground.

---

# 19. Use Walk-Forward Testing

Promising patterns should eventually be tested chronologically.

For example:

`Research past → establish rules → test next period → move forward → repeat`

This better approximates how the strategy would have encountered markets in reality.

Future data must never influence earlier decisions.

---

# 20. Test Across Market Regimes

Patterns should be evaluated separately during different environments where possible.

Examples:

* bull markets
* bear markets
* corrections
* recoveries
* high volatility
* low volatility
* rising rates
* falling rates
* recessions
* expansions

A pattern working only during one extraordinary bull market should not automatically be considered robust.

---

# 21. Test Across Assets

A pattern discovered on one ETF may simply describe that ETF.

Whenever appropriate, test promising patterns across:

* broad-market ETFs
* sector ETFs
* industries
* different volatility profiles
* different economic exposures

Patterns that generalize deserve greater attention.

---

# 22. Sample Size Must Always Be Visible

Every result must include its number of observations.

Never report:

> **72% win rate**

without also reporting:

> **72% win rate — 3,482 observations**

Probability without sample size is incomplete information.

Very small samples must be clearly identified.

---

# 23. Correlated Observations Are Not Fully Independent

Ten sector ETFs rising during the same market rally do not necessarily represent ten completely independent confirmations.

Likewise, overlapping 20-day holding periods may represent largely the same market event.

Observation counts must therefore not automatically be interpreted as independent trials.

Where material, clustering and overlapping observations should be investigated.

---

# 24. Capital Preservation Comes First

Stockball's research priority is:

> **Capital Preservation → Probability → Return**

Experiments should therefore emphasize downside as strongly as upside.

Primary risk measurements should include where appropriate:

* loss rate
* median loss
* average loss
* worst outcome
* bottom 10% outcome
* bottom 5% outcome
* maximum adverse excursion
* drawdown
* volatility

A strategy with attractive average returns but catastrophic tail losses may violate the Stockball philosophy.

---

# 25. Win Rate Alone Is Not Enough

A strategy winning 90% of the time can still lose money if its occasional losses are enormous.

Therefore every probability statistic must be considered alongside the magnitude of gains and losses.

At minimum:

`Probability × Magnitude × Downside`

must be examined together.

---

# 26. Median Matters

Extreme market events can heavily distort averages.

Where appropriate, results should report both:

* mean
* median

The difference between them may itself contain useful information about the distribution of outcomes.

---

# 27. Examine the Distribution

Do not reduce an experiment to one number.

Where useful, examine:

* percentiles
* distribution shape
* extreme outcomes
* positive/negative tails
* volatility
* clustering
* regime differences

Two patterns with identical average returns can have radically different risk characteristics.

---

# 28. Measure What Happened During the Trade

Final return alone does not describe the experience of holding an asset.

Where possible, measure:

### Maximum Adverse Excursion — MAE

How far did the position move against us before the holding period ended?

### Maximum Favorable Excursion — MFE

How far did the position move in our favor?

This can later help investigate sensible exits, stop-losses, and profit-taking rules without guessing.

---

# 29. Transaction Costs Eventually Count

Early exploratory research may show gross returns.

Any pattern progressing toward practical consideration must account for realistic:

* spreads
* commissions where applicable
* slippage
* taxes where relevant to the intended use
* other execution costs

The more frequently a strategy trades, the more important these become.

Gross performance must never be presented as equivalent to realizable performance.

---

# 30. Execution Must Be Possible

A historical strategy cannot assume execution at a price unavailable to a real investor.

If a signal requires closing-price information, we cannot simultaneously assume we purchased at that same closing price unless the methodology realistically supports doing so.

Execution assumptions must be documented.

---

# 31. Liquidity Matters

A theoretical pattern is less valuable if positions could not realistically be entered or exited.

As the project expands, relevant liquidity measures may include:

* average daily volume
* dollar volume
* bid/ask spread
* ETF assets under management

For our initial major ETF research, this risk may be relatively small but should never be forgotten.

---

# 32. No Forced Trades

The system is not required to find an opportunity.

If no pattern meets the eventual required statistical and risk criteria:

> **WAIT**

is a valid research conclusion.

The number of days producing no qualifying signal should eventually be measured rather than treated as a problem.

---

# 33. Do Not Optimize for Activity

More trades do not automatically produce better results.

Stockball should optimize for the quality of evidence, not the quantity of transactions.

One strong opportunity may be preferable to twenty marginal opportunities.

---

# 34. Pattern Discovery and Trading Rules Are Different Research Problems

Discovering:

> "This situation historically produced favorable outcomes."

does not automatically answer:

* when to enter
* position size
* when to exit
* stop-loss level
* profit target
* portfolio allocation

Those questions require separate experiments.

Do not silently introduce trading rules into pattern-discovery experiments.

---

# 35. AI Generates Hypotheses — Evidence Judges Them

AI may help:

* generate hypotheses
* write research code
* identify possible variables
* summarize results
* identify anomalies
* suggest follow-up experiments

AI does not decide whether a pattern is valid.

The evidence does.

AI-generated code must also be reviewed for methodological errors.

---

# 36. Code Must Be Reproducible

Research code should favor:

* clarity
* deterministic calculations
* documented assumptions
* reusable calculations
* version control
* traceable outputs

Clever code is less valuable than code we can understand and verify six months later.

---

# 37. Results Must Be Reproducible

Every experiment should retain enough information to reproduce its findings.

At minimum:

`Experiment ID`

`Specification Version`

`Dataset Version`

`Assets`

`Date Range`

`Signal Rules`

`Outcome Rules`

`Execution Assumptions`

`Code Version`

`Results`

`Conclusion`

---

# 38. Results Must Be Recorded Before Interpretation Changes

Once an experiment finishes, save its raw result before discussing modifications or follow-up ideas.

This creates separation between:

**What happened**

and

**What we think it means.**

Both should be recorded.

They should not be confused.

---

# 39. Conclusions Have Confidence Levels

Experiments should not simply be labeled:

`Works / Doesn't Work`

Prefer classifications such as:

* Rejected
* Inconclusive
* Weak Evidence
* Interesting
* Strong Candidate
* Validation Required
* Failed Validation
* Robust Candidate

Language should reflect uncertainty.

---

# 40. Extraordinary Results Receive More Scrutiny

If an experiment produces results that look exceptionally good, our first reaction should not be excitement.

It should be:

> **What could be wrong?**

Check:

* data leakage
* look-ahead bias
* calculation errors
* tiny samples
* survivorship bias
* unrealistic execution
* duplicated observations
* overfitting
* regime concentration

The better the result looks, the harder we try to disprove it.

---

# 41. Do Not Fall in Love With Patterns

A pattern has no loyalty to us.

Past success does not guarantee future persistence.

Markets evolve.

Relationships disappear.

Participants adapt.

Structural changes occur.

Even validated patterns must eventually be monitored for deterioration.

---

# 42. Research Before Capital

The progression toward any real-world application is:

> **Historical Discovery → Historical Validation → Walk-Forward Testing → Paper Trading → Extended Observation → Small Real-World Testing**

No stage automatically earns progression to the next.

Stockball has no deadline requiring real capital deployment.

---

# 43. The Researcher's Final Test

Before accepting an exciting result, ask:

1. **Did we know the rules before seeing the answer?**
2. **Could future information have leaked into the signal?**
3. **Is the sample large enough to matter?**
4. **Did we compare against an appropriate baseline?**
5. **Does it survive different periods and market regimes?**
6. **Does it survive outside the data used to discover it?**
7. **Are the losses acceptable?**
8. **Could the strategy realistically have been executed?**
9. **Can someone reproduce the result?**
10. **Have we genuinely tried to prove ourselves wrong?**

If we cannot answer these questions satisfactorily, the pattern is not ready.

---

# The Stockball Research Rule

> ## Never ask the data to prove us right.
>
> ## Ask the data whether we are wrong.

Our job is not to manufacture a profitable backtest.

Our job is to discover whether a measurable advantage exists **after we have done everything reasonably possible to make that advantage disappear.**
