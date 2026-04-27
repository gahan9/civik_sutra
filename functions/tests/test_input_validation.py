from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models.chat import ChatRequest
from src.models.booth import NearbyRequest, DirectionsRequest
from src.models.candidate import CompareRequest, CandidateSearchRequest
from src.models.manifesto import ManifestoCompareRequest


def test_nearby_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        NearbyRequest.model_validate(
            {
                "lat": 28.6,
                "lng": 77.2,
                "radius_km": 5,
                "unknown_field": "malicious_payload",
            }
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_directions_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        DirectionsRequest.model_validate(
            {
                "origin": {"lat": 28.6, "lng": 77.2},
                "destination": {"lat": 28.7, "lng": 77.3},
                "mode": "driving",
                "hacked": True,
            }
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_candidate_search_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CandidateSearchRequest.model_validate(
            {"constituency": "Delhi", "inject_sql": "DROP TABLE users"}
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_compare_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CompareRequest.model_validate(
            {"candidate_ids": ["cand_1", "cand_2"], "extra_param": 123}
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_manifesto_compare_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ManifestoCompareRequest.model_validate(
            {
                "party_names": ["BJP", "INC"],
                "categories": ["economy"],
                "include_past_promises": True,
                "malicious_key": "value",
            }
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_chat_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ChatRequest.model_validate(
            {
                "message": "Hello",
                "session_id": "12345",
                "language": "en",
                "location": {"lat": 28.6, "lng": 77.2},
                "unauthorized_access": True,
            }
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_chat_request_validates_message_length() -> None:
    # Too short
    with pytest.raises(ValidationError):
        ChatRequest.model_validate({"message": "", "session_id": "12345"})

    # Too long
    with pytest.raises(ValidationError):
        ChatRequest.model_validate({"message": "A" * 2001, "session_id": "12345"})


def test_chat_request_validates_language() -> None:
    with pytest.raises(ValidationError):
        ChatRequest.model_validate(
            {"message": "Hello", "session_id": "123", "language": "fr"}
        )
