from __future__ import annotations


import asyncio
import json
from typing import Any

from firebase_functions import https_fn
from pydantic import ValidationError

from src.models.booth import DirectionsRequest, NearbyRequest
from src.models.candidate import (
    CandidateSearchRequest,
    CompareRequest,
)
from src.models.chat import ChatRequest
from src.models.manifesto import ManifestoCompareRequest
from src.services.candidate_service import CandidateService
from src.services.chat_service import ChatService
from src.services.geo_service import GeoService
from src.services.manifesto_service import ManifestoService


@https_fn.on_request(region="asia-south1")
def api(req: Any) -> Any:
    """Execute api operation."""
    if req.method == "OPTIONS":
        return _response({}, status=204)

    geo = GeoService()
    candidate_svc = CandidateService()
    manifesto_svc = ManifestoService()
    chat_svc = ChatService()
    path = req.path.rstrip("/") or "/"

    try:
        if req.method == "GET" and path == "/health":
            return _response({"status": "ok"})

        if req.method == "POST" and path == "/booth/nearby":
            nearby_payload = NearbyRequest.model_validate(
                req.get_json(silent=True) or {}
            )
            nearby_result = asyncio.run(
                geo.find_nearby_booths(
                    lat=nearby_payload.lat,
                    lng=nearby_payload.lng,
                    radius_km=nearby_payload.radius_km,
                )
            )
            return _response(nearby_result.model_dump())

        if req.method == "POST" and path == "/booth/directions":
            dir_payload = DirectionsRequest.model_validate(
                req.get_json(silent=True) or {}
            )
            dir_result = asyncio.run(geo.get_directions(dir_payload))
            return _response(dir_result.model_dump())

        if req.method == "GET" and path.startswith("/booth/verify/"):
            epic_number = path.rsplit("/", maxsplit=1)[-1]
            verify_result = asyncio.run(geo.verify_booth_assignment(epic_number))
            return _response(verify_result.model_dump())

        if req.method == "POST" and path == "/candidate/search":
            search_payload = CandidateSearchRequest.model_validate(
                req.get_json(silent=True) or {},
            )
            if search_payload.constituency:
                search_result = asyncio.run(
                    candidate_svc.search_by_constituency(search_payload.constituency),
                )
            elif search_payload.lat is not None and search_payload.lng is not None:
                search_result = asyncio.run(
                    candidate_svc.search_by_location(
                        search_payload.lat, search_payload.lng
                    ),
                )
            else:
                return _response(
                    {"detail": "Missing constituency or location"}, status=400
                )
            return _response(search_result.model_dump())

        if (
            req.method == "GET"
            and path.startswith("/candidate/")
            and path.endswith("/background")
        ):
            candidate_id = path.split("/")[2]
            bg_result = asyncio.run(candidate_svc.background_check(candidate_id))
            return _response(bg_result.model_dump())

        if req.method == "POST" and path == "/candidate/compare":
            comp_payload = CompareRequest.model_validate(
                req.get_json(silent=True) or {},
            )
            comp_result = asyncio.run(candidate_svc.compare(comp_payload.candidate_ids))
            return _response(comp_result.model_dump())

        if req.method == "POST" and path == "/manifesto/compare":
            m_comp_payload = ManifestoCompareRequest.model_validate(
                req.get_json(silent=True) or {},
            )
            m_comp_result = asyncio.run(
                manifesto_svc.compare_manifestos(
                    party_names=m_comp_payload.party_names,
                    categories=m_comp_payload.categories,
                    include_past_promises=m_comp_payload.include_past_promises,
                )
            )
            return _response(m_comp_result.model_dump())

        if req.method == "POST" and path == "/assistant/chat":
            chat_payload = ChatRequest.model_validate(
                req.get_json(silent=True) or {},
            )
            chat_result = asyncio.run(
                chat_svc.chat(
                    message=chat_payload.message,
                    session_id=chat_payload.session_id,
                    language=chat_payload.language,
                )
            )
            return _response(chat_result.model_dump())

        if req.method == "GET" and path == "/assistant/questions":
            lang = req.args.get("language", "en")
            questions = chat_svc.get_quick_questions(lang)
            return _response({"questions": questions})

    except ValidationError as error:
        return _response({"detail": error.errors()}, status=422)

    return _response({"detail": "Not found"}, status=404)


def _response(payload: dict[str, Any], status: int = 200) -> Any:
    # Use environment variable for CORS origin, default to production URL
    import os

    cors_origin = os.getenv(
        "EP_CORS_ORIGINS", '["https://civiksutra-2604261729.web.app"]'
    )
    try:
        origins = json.loads(cors_origin)
        origin = (
            origins[0]
            if isinstance(origins, list) and origins
            else "https://civiksutra-2604261729.web.app"
        )
    except json.JSONDecodeError:
        origin = "https://civiksutra-2604261729.web.app"

    return https_fn.Response(  # type: ignore[attr-defined]
        json.dumps(payload),
        status=status,
        headers={
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Origin": origin,
            "Content-Type": "application/json",
        },
    )
