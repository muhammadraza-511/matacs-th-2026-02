
from evaluator import (
    Proposal,
    check_mandatory,
    score_experience,
    score_price,
    score_timeline,
    score_warranty,
    evaluate_proposals,
)


def test_experience_score():
    assert score_experience(10) == 100
    assert score_experience(5) == 50
    assert score_experience(15) == 100


def test_price_score():
    assert score_price(200000, 200000) == 100
    assert round(score_price(250000, 200000), 2) == 80
    assert score_price(260001, 200000) is None


def test_timeline_score():
    assert score_timeline(16) == 0
    assert score_timeline(8) == 50
    assert score_timeline(17) is None


def test_warranty_score():
    assert score_warranty(25, 10) == 100
    assert score_warranty(25, 5) == 75


def test_mandatory_failure():
    proposal = Proposal(
        proposal_id="B",
        bidder_license=False,
        wsib_clearance=True,
        insurance_5m=True,
    )

    assert check_mandatory(proposal) == "ineligible"


def test_missing_mandatory_evidence():
    proposal = Proposal(
        proposal_id="X",
        bidder_license=None,
        wsib_clearance=True,
        insurance_5m=True,
    )

    assert check_mandatory(proposal) == "flagged"


def test_missing_timeline_is_flagged():
    proposal = Proposal(
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
        defined_crew=True,
        safety_plan=True,
        monitoring_plan=True,
    )

    result = evaluate_proposals([proposal])

    assert result[0]["status"] == "flagged"
    assert result[0]["score"] is None
    assert result[0]["rank"] is None


def test_complete_proposals_are_ranked_with_criterion_scores():
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

    result = evaluate_proposals(proposals)

    assert result[0]["rank"] == 1
    assert result[0]["score"] == 88.75
    assert result[0]["criterion_scores"]["price"] == 100
    assert result[1]["rank"] == 2
    assert result[1]["score"] == 81.35
