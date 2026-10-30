# MATACS-TH-2026-02 — System Design Writeup

## 1. What should AI do, and what should plain code do?

I would use a hybrid AI and rule-based architecture, with explicit failure
paths and human checkpoints as shown in the workflow diagram.

AI is best suited for understanding unstructured proposal documents. It would extract relevant information such as contractor licence details, WSIB clearance, insurance coverage, project experience, pricing, completion timelines, warranties, and team information. It would return structured JSON containing extracted values, supporting evidence, page references, and confidence information.

Plain backend code would handle authentication and role checks, file and security
validation, PDF extraction, schema and evidence validation, mandatory
requirement checks, weighted scoring, ranking, retries, and audit logging.
These operations require predictable and repeatable results, so they should not
depend on LLM-generated decisions. Unreadable PDFs go through OCR or manual
review, and invalid model JSON is retried safely or flagged rather than
silently accepted.

For example, the LLM may extract a completion timeline of 12 weeks, but Python validates the value and calculates its score using the active scoring configuration. The LLM does not decide which proposal wins.

## 2. How would you make the results consistent and explainable?

I would use structured AI outputs with a predefined schema and validate them using Pydantic. Every extracted value should have supporting evidence and a source page reference so reviewers can verify the information against the original proposal.

The backend would calculate scores using deterministic formulas and administrator-configured weights. The same validated inputs, proposal set, and criteria version would therefore produce the same ranking.

I would also record the model identifier, prompt version, extracted information, criteria version, individual criterion scores, and final evaluation result. This makes results traceable and allows reviewers to understand how each score was calculated.

AI confidence would be used as a review signal rather than proof of correctness.

## 3. Where should a human reviewer be involved?

Human oversight is required whenever the system encounters missing, ambiguous, or conflicting evidence.

For example, if a proposal mentions a licensed subcontractor but does not
establish that the bidder itself holds the required Ontario electrical
contractor licence, the system should not automatically treat the requirement
as satisfied. Under the strict assessment interpretation, Proposal B is
ineligible because the proposal says the subcontractor will be confirmed only
after award; genuinely unclear or absent evidence in other proposals is
flagged for clarification.

Reviewers should be able to inspect extracted evidence, request clarification, confirm results, and override an evaluation when justified. Every override must include a reason and be recorded with the reviewer identity and timestamp.

The final procurement award must always remain a human decision. The system provides decision support, not autonomous award selection.

## 4. What happens if an administrator changes the evaluation criteria?

I would implement criteria versioning.

Whenever an administrator changes a criterion, scoring formula, or weight, the system creates a new configuration version rather than overwriting the previous one.

Existing evaluations remain associated with the criteria version used when they were originally calculated. New evaluations use the newly activated version.

If an administrator wants to evaluate existing proposals against updated criteria, the system creates a new evaluation while preserving the original result. This ensures historical rankings remain explainable and auditable.

The backend should also validate that weighted criteria total 100% before activating a configuration.

## 5. What are the main risks, and how would you address them?

**Incorrect extraction or hallucination:** An LLM may extract an incorrect price, timeline, or licence detail. I would require supporting evidence, validate the response schema, use confidence thresholds to trigger review, and allow reviewers to compare extracted facts with the source document.

**Prompt injection:** A proposal may contain instructions attempting to influence the AI ranking. Uploaded content must be treated as untrusted data. System instructions remain separate, and the backend—not the LLM—controls eligibility and scoring.

**Missing or ambiguous information:** The system must distinguish between a confirmed failure and information that was not provided. Missing evidence should be flagged for clarification rather than automatically interpreted as a negative answer.

**Inconsistent or biased evaluation:** Fixed scoring formulas, configurable criteria, versioned configurations, and human review reduce inconsistent decisions. Reviewers should be able to inspect the evidence behind every criterion score.

**Security and operational risks:** Authentication and role-based access should
protect admin, reviewer, and proposal data. Uploaded documents are untrusted
input and API credentials must remain outside source control. File-type and
size limits, malware scanning, request limits, timeouts, safe retries,
idempotent jobs, and monitoring should protect against operational failures and
excessive AI usage. Model, prompt, and criteria versions are logged with
provenance so every evaluation can be reproduced.

Overall, I would design the application as an explainable decision-support system in which AI assists with document understanding while deterministic backend rules and human oversight control the evaluation process.