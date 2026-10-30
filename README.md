# MATACS — Associate Software Developer Assessment

**Reference:** MATACS-TH-2026-02

**Candidate:** Muhammad Raza

**Time spent:** 2 hours

## Project Overview

This repository contains the system design and optional Python prototype for an AI-assisted commercial solar proposal triage system.

The proposed application extracts information from submitted proposals, validates mandatory requirements, calculates weighted evaluation scores and generates explainable rankings for human review.

The final award decision remains under human control.

## Repository Structure

| File | Description |
|---|---|
| `DESIGN_NOTES.md` | Architecture and database design |
| `SCORING_SPEC.md` | Scoring formulas and evaluation rules |
| `WRITEUP.md` | Answers to the five assessment questions |
| `PROMPTS.md` | AI extraction prompts and safeguards |
| `ranking.json` | Evaluation results for proposals A–E |
| `diagram/process-flow.png` | End-to-end system workflow diagram |
| `diagram/diagramCode.txt` | Editable Mermaid diagram source |
| `prototype/` | Python evaluation prototype and tests |

## Technology Choices

- Python
- FastAPI (proposed backend architecture)
- Pydantic
- PostgreSQL (proposed database)
- OpenAI API (proposed AI integration)
- PyMuPDF
- Pytest

## Running the Prototype

Install dependencies:

```bash
pip install -r prototype/requirement.txt
```

Run the evaluation:

```bash
python prototype/evaluator.py
```

Run tests:

```bash
cd prototype
pytest -v
```

## AI Tool Usage

I used ChatGPT to assist with system architecture brainstorming, scoring design, prompt engineering and documentation. I reviewed the generated suggestions rather than accepting them blindly. For example, I retained the strict assessment interpretation that Proposal B is ineligible: its own licence is not established and it says the licensed subcontractor will only be confirmed after award, which does not satisfy the bidder-licence requirement.

## Assessment Deliverables

- [System Design Notes](DESIGN_NOTES.md)
- [Scoring Specification](SCORING_SPEC.md)
- [Assessment Writeup](WRITEUP.md)
- [AI Prompts](PROMPTS.md)
- [Proposal Rankings](ranking.json)
- [Workflow Diagram](diagram/process-flow.png)
- [Python Prototype](prototype/)
