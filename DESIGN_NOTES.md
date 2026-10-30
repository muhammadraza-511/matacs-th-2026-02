# MATACS-TH-2026-02 — System Design Notes

## 1. Project Overview

The proposed system is an AI-assisted proposal triage application for evaluating commercial solar installation proposals.

The system allows administrators to configure evaluation categories and criteria, reviewers to upload proposals, and the application to extract relevant information, validate mandatory requirements, calculate weighted scores, and generate an explainable ranking.

The final award decision remains with a human reviewer.

## 2. Proposed Technology Stack

| Component | Technology |
|---|---|
| Backend API | Python + FastAPI |
| AI integration | OpenAI API |
| PDF text extraction | PyMuPDF |
| Data validation | Pydantic |
| Database | PostgreSQL |
| Background processing | Celery + Redis |
| Testing | Pytest |
| Version control | Git + GitHub |

The architecture will use a modular backend rather than separate microservices because the assessment does not require distributed infrastructure.

## 3. Main System Components

### 3.1 Configuration Management

Administrators can:

- Create and manage evaluation categories.
- Define mandatory pass/fail requirements.
- Configure weighted evaluation criteria.
- Set scoring rules and weight percentages.
- Update criteria without modifying application code.

Criteria and scoring configurations will be stored in the database rather than hard-coded.

### 3.2 Proposal Processing

Reviewers can:

- Upload proposal documents.
- Select the relevant evaluation category.
- Submit proposals for evaluation.

The backend validates uploaded files and extracts their text using PDF processing tools.

The extracted text is sent to an AI model, which identifies relevant proposal information and returns structured JSON containing extracted values, supporting evidence, and confidence information.

### 3.3 Evaluation Engine

The backend:

- Validates AI-generated information.
- Checks mandatory requirements.
- Identifies missing or ambiguous evidence.
- Calculates individual criterion scores.
- Applies configured weights.
- Generates the final ranking.

The scoring and ranking calculations will be deterministic backend operations, not decisions delegated to the LLM.

### 3.4 Human Review and Audit

Reviewers can:

- Inspect extracted information and supporting evidence.
- Review scores and ranking explanations.
- Investigate flagged proposals.
- Override evaluation results with a recorded reason.
- Confirm the final evaluation decision.

The system records important actions and changes in audit logs.

## 4. Proposed Database Design

The application will use PostgreSQL.

| Entity | Purpose |
|---|---|
| users | Stores administrator and reviewer accounts |
| categories | Stores evaluation categories |
| criteria_versions | Stores versions of evaluation configurations |
| criteria | Stores mandatory and weighted criteria |
| proposals | Stores proposal metadata and file references |
| extracted_facts | Stores AI-extracted information and evidence |
| evaluations | Stores proposal evaluation results |
| criterion_scores | Stores individual criterion scores |
| audit_logs | Records user actions and evaluation changes |

### Entity Relationships

- A category can have multiple criteria versions.
- Each criteria version contains multiple criteria.
- A category can receive multiple proposals.
- Each proposal can have extracted facts and multiple evaluation records.
- Each evaluation references the criteria version used.
- Each evaluation contains individual criterion scores.
- User actions are recorded in audit logs.

## 5. Criteria Versioning

Evaluation criteria must be versioned to preserve historical results.

For example:

- Version 1: Original evaluation weights.
- Version 2: Updated evaluation weights.

When an administrator changes a criterion or weight, the system creates a new configuration version rather than modifying the previous version.

Existing evaluation results retain their original criteria version. New evaluations use the latest active version.

If an administrator requests re-evaluation, the system creates a new evaluation using the updated configuration while preserving the previous result.

## 6. Evaluation Criteria

The assessment defines the following mandatory requirements:

1. The bidder must hold and state an Ontario electrical contractor licence.
2. WSIB clearance and $5M liability insurance must both be confirmed in the proposal.

The weighted criteria total 100%:

| Criterion | Weight |
|---|---:|
| Relevant experience | 30% |
| Price | 25% |
| Timeline | 15% |
| Warranty | 15% |
| Team and approach | 15% |
| **Total** | **100%** |

Mandatory requirements are evaluated separately from weighted scoring.

A confirmed mandatory failure makes a proposal ineligible. Missing or ambiguous evidence is flagged for human review rather than automatically treated as a confirmed failure.

## 7. AI Extraction and Evidence

The AI model extracts relevant information from proposal documents and returns structured data.

Each extracted fact should contain:

- Extracted value.
- Supporting evidence from the proposal.
- Confidence information.
- Missing or uncertain information where applicable.

Example:

```json
{
  "price": {
    "value": 238000,
    "currency": "CAD",
    "evidence": "Total project cost: $238,000 CAD",
    "confidence": 0.98
  }
}
```

The backend validates the returned structure using Pydantic and checks that the evidence supports the extracted information.

The AI model does not independently determine eligibility or calculate final weighted scores.

## 8. Proposed Evaluation Workflow

1. Administrator creates an evaluation category.
2. Administrator configures mandatory and weighted criteria.
3. Reviewer uploads a proposal.
4. Backend validates the uploaded file.
5. PDF text is extracted.
6. If extraction fails, the document is routed through OCR or manual review before processing continues.
7. AI extracts structured proposal information and evidence.
8. Backend validates the extracted information. Invalid JSON is retried safely or flagged.
9. Evidence, data types, uncertainty, and provenance are validated and stored.
10. Mandatory requirements are checked.
11. Missing or ambiguous information is flagged.
12. Proposals with complete scoring evidence are scored using deterministic backend rules. Missing or invalid scoring data is flagged rather than scored.
13. The system generates criterion-level explanations and ranked results.
14. Human reviewer examines and confirms or overrides the evaluation.
15. Final decisions and relevant actions are recorded in audit logs.

Authentication, role-based access, untrusted-input handling, credential
protection, and model/prompt/criteria version logging apply across the workflow.

The sample scoring configuration uses these formulas:

- Experience: `min(qualifying_projects / 10, 1) * 100`.
- Price: `lowest_compliant_price / proposal_price * 100`, using only eligible bids at or below $260,000 CAD.
- Timeline: `((16 - completion_weeks) / 16) * 100`; missing or out-of-range values are flagged.
- Warranty: average of panel score capped at 25 years and workmanship score capped at 10 years.
- Team and approach: 25 points each for a named lead, defined crew, safety plan, and monitoring plan.

The final score is the weighted sum using the configured 30%, 25%, 15%, 15%, and 15% weights. These formulas are versioned configuration, not hard-coded business decisions.

## 9. Initial Edge-Case Decisions

### Proposal B — Electrical Contractor Licence

The proposal states that electrical work will be performed by a licensed subcontractor, with the subcontractor to be confirmed after contract award.

The mandatory requirement specifically requires the bidder to hold and state its own Ontario electrical contractor licence.

Under a strict interpretation, the bidder's own licence is not established. The proposal will therefore be treated as ineligible unless the reviewer obtains evidence satisfying the requirement.

### Proposal D — Missing Completion Timeline

The proposal states that the schedule will be determined after a detailed site assessment.

The system must not invent a completion timeline or assign an assumed timeline score.

The proposal will be flagged for clarification because the completion period cannot currently be evaluated.

## 10. Design Principles

The system follows these principles:

- **Configurable:** Evaluation criteria are managed through the admin interface and database.
- **Explainable:** Scores are supported by evidence and understandable reasons.
- **Deterministic:** Identical validated inputs and criteria versions produce identical scoring results.
- **Human-controlled:** AI assists evaluation but does not make the final award decision.
- **Auditable:** Evaluation results, configuration versions, and human overrides are recorded.
- **Secure:** Uploaded proposal content is treated as untrusted input, including instructions embedded in documents.
