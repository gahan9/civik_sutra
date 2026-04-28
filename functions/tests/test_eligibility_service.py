from __future__ import annotations

from src.services.eligibility_service import check_voter_eligibility


def test_eligible_indian_resident() -> None:
    result = check_voter_eligibility(age=21, citizenship="indian")
    assert result["eligible"] is True
    assert "electoralsearch" in str(result["next_step"]).lower()


def test_eligible_nri() -> None:
    result = check_voter_eligibility(
        age=30, citizenship="nri", residence="abroad"
    )
    assert result["eligible"] is True
    assert "form 6a" in str(result["next_step"]).lower()


def test_ineligible_underage() -> None:
    result = check_voter_eligibility(age=16, citizenship="indian")
    assert result["eligible"] is False
    assert "minimum voting age" in str(result["reason"]).lower()


def test_ineligible_foreign_citizen() -> None:
    result = check_voter_eligibility(age=40, citizenship="foreign")
    assert result["eligible"] is False
    assert "indian citizens" in str(result["reason"]).lower()


def test_ineligible_underage_and_foreign() -> None:
    result = check_voter_eligibility(age=10, citizenship="foreign")
    assert result["eligible"] is False
    assert "minimum voting age" in str(result["reason"]).lower()
    assert "indian citizens" in str(result["reason"]).lower()
