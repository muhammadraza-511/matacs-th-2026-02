
from typing import Optional
from pydantic import BaseModel, Field
import json


# -----------------------------
# 1. Data Models
# -----------------------------

class Proposal(BaseModel):
    proposal_id: str

    # Mandatory requirements
    bidder_license: Optional[bool] = None
    wsib_clearance: Optional[bool] = None
    insurance_5m: Optional[bool] = None

    # Weighted criteria
    experience_projects: Optional[int] = None
    price: Optional[float] = None
    timeline_weeks: Optional[int] = None

    panel_warranty: Optional[int] = None
    workmanship_warranty: Optional[int] = None

    named_lead: Optional[bool] = None
    defined_crew: Optional[bool] = None
    safety_plan: Optional[bool] = None
    monitoring_plan: Optional[bool] = None


# -----------------------------
# 2. Evaluation Configuration
# -----------------------------

WEIGHTS = {
    "experience": 0.30,
    "price": 0.25,
    "timeline": 0.15,
    "warranty": 0.15,
    "team": 0.15,
}


# -----------------------------
# 3. Mandatory Validation
# -----------------------------

def check_mandatory(proposal: Proposal):
    checks = [
        proposal.bidder_license,
        proposal.wsib_clearance,
        proposal.insurance_5m,
    ]

    if False in checks:
        return "ineligible"

    if None in checks:
        return "flagged"

    return "eligible"


# -----------------------------
# 4. Scoring Functions
# -----------------------------

def score_experience(projects):
    if projects is None:
        return None

    return min(projects / 10, 1) * 100


def score_price(price, lowest_price):
    if (
        price is None
        or price <= 0
        or price > 260000
        or lowest_price is None
    ):
        return None

    return (lowest_price / price) * 100


def score_timeline(weeks):
    if weeks is None:
        return None

    if weeks > 16 or weeks <= 0:
        return None

    return ((16 - weeks) / 16) * 100


def score_warranty(panel, workmanship):
    if panel is None or workmanship is None:
        return None

    panel_score = min(panel / 25, 1) * 100
    workmanship_score = min(workmanship / 10, 1) * 100

    return (panel_score + workmanship_score) / 2


def score_team(proposal):
    components = [
        proposal.named_lead,
        proposal.defined_crew,
        proposal.safety_plan,
        proposal.monitoring_plan,
    ]

    # Missing information requires human clarification.
    if any(value is None for value in components):
        return None

    return sum(components) / len(components) * 100


# -----------------------------
# 5. Evaluation Engine
# -----------------------------

def evaluate_proposals(proposals):

    # Determine the lowest price among proposals
    # that pass all mandatory requirements.
    compliant_prices = [
        p.price
        for p in proposals
        if check_mandatory(p) == "eligible"
        and p.price is not None
        and p.price > 0
        and p.price <= 260000
    ]

    lowest_price = (
        min(compliant_prices)
        if compliant_prices else None
    )

    results = []

    for proposal in proposals:

        status = check_mandatory(proposal)

        result = {
            "proposal_id": proposal.proposal_id,
            "status": status,
            "rank": None,
            "score": None,
            "criterion_scores": None,
            "reason": "",
        }

        if status == "ineligible":
            result["reason"] = (
                "A mandatory requirement failed."
            )
            results.append(result)
            continue

        if status == "flagged":
            result["reason"] = (
                "Mandatory requirement evidence is missing."
            )
            results.append(result)
            continue

        # Calculate individual criterion scores.
        scores = {
            "experience": score_experience(
                proposal.experience_projects
            ),
            "price": score_price(
                proposal.price, lowest_price
            ),
            "timeline": score_timeline(
                proposal.timeline_weeks
            ),
            "warranty": score_warranty(
                proposal.panel_warranty,
                proposal.workmanship_warranty
            ),
            "team": score_team(proposal),
        }

        missing = [
            name for name, value in scores.items()
            if value is None
        ]

        if missing:
            result["status"] = "flagged"
            result["reason"] = (
                "Missing or invalid scoring evidence: "
                + ", ".join(missing)
            )
            results.append(result)
            continue

        total = sum(
            scores[name] * WEIGHTS[name]
            for name in WEIGHTS
        )

        result["status"] = "ranked"
        result["score"] = round(total, 2)
        result["criterion_scores"] = {
            name: round(value, 2)
            for name, value in scores.items()
        }
        result["reason"] = (
            "Passed mandatory checks; deterministic criterion scores "
            "were weighted using the published criteria version."
        )

        results.append(result)

    # Rank only proposals with final scores.
    ranked = [
        item for item in results
        if item["status"] == "ranked"
    ]

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    for position, item in enumerate(ranked, start=1):
        item["rank"] = position

    return results


# -----------------------------
# 6. Sample Input
# -----------------------------

if __name__ == "__main__":

    proposals = [
        Proposal(
            proposal_id="A",
            bidder_license=True,
            wsib_clearance=True,
            insurance_5m=True,
            experience_projects=14,
            price=238000,
            timeline_weeks=12,
            panel_warranty=25,
            workmanship_warranty=10,
            named_lead=True,
            defined_crew=True,
            safety_plan=True,
            monitoring_plan=True,
        ),

        Proposal(
            proposal_id="B",
            bidder_license=False,  # Strict interpretation
            wsib_clearance=True,
            insurance_5m=True,
            experience_projects=6,
            price=189500,
            timeline_weeks=10,
            panel_warranty=25,
            workmanship_warranty=5,
        ),

        Proposal(
            proposal_id="C",
            bidder_license=True,
            wsib_clearance=True,
            insurance_5m=True,
            experience_projects=9,
            price=244000,
            timeline_weeks=14,
            panel_warranty=25,
            workmanship_warranty=10,
            named_lead=True,
            defined_crew=True,
            safety_plan=None,
            monitoring_plan=None,
        ),

        Proposal(
            proposal_id="D",
            bidder_license=True,
            wsib_clearance=True,
            insurance_5m=True,
            experience_projects=11,
            price=231000,
            timeline_weeks=None,
            panel_warranty=25,
            workmanship_warranty=10,
            named_lead=True,
            defined_crew=None,
            safety_plan=True,
            monitoring_plan=None,
        ),

        Proposal(
            proposal_id="E",
            bidder_license=True,
            wsib_clearance=True,
            insurance_5m=True,
            experience_projects=8,
            price=242500,
            timeline_weeks=13,
            panel_warranty=25,
            workmanship_warranty=12,
            named_lead=True,
            defined_crew=True,
            safety_plan=True,
            monitoring_plan=True,
        ),
    ]

    output = evaluate_proposals(proposals)

    print(json.dumps(output, indent=4))
