# Scoring Specification

These formulas are the versioned configuration used by the optional prototype.
Mandatory requirements are evaluated before weighted scoring.

## Mandatory requirements

- The bidder itself must state an Ontario electrical contractor licence.
- The proposal must confirm both WSIB clearance and $5M liability insurance.

A confirmed mandatory failure is `ineligible`. Missing or unclear evidence is
normally `flagged`; Proposal B is the assessment's strict exception because it
explicitly defers the bidder's electrical work to a subcontractor that will be
selected after award.

## Weighted criteria

Weights total 100%:

| Criterion | Weight | Formula |
| --- | ---: | --- |
| Relevant experience | 30% | `min(qualifying_projects / 10, 1) * 100` |
| Price | 25% | `lowest_compliant_price / proposal_price * 100` |
| Timeline | 15% | `((16 - completion_weeks) / 16) * 100` |
| Warranty | 15% | Average of panel and workmanship component scores |
| Team and approach | 15% | Four documented components worth 25 points each |

Price uses only eligible proposals priced at or below $260,000 CAD. Panel
warranty is capped at 25 years and workmanship warranty at 10 years. Timeline
values over 16 weeks, missing values, and missing scoring evidence are not
invented; the proposal is flagged for human review.

The final score is:

```text
(experience * 0.30) +
(price * 0.25) +
(timeline * 0.15) +
(warranty * 0.15) +
(team * 0.15)
```

The engine stores each criterion score, the criteria-version identifier, and
the evidence used to calculate it.
