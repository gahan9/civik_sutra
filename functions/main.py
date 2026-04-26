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
from src.models.manifesto import ManifestoCompareRequest
from src.services.candidate_service import CandidateService
from src.services.geo_service import GeoService
from src.services.manifesto_service import ManifestoService


@https_fn.on_request(region="asia-south1")
def api(req: https_fn.Request) -> https_fn.Response:
    if req.method == "OPTIONS":
        return _response({}, status=204)

    geo = GeoService()
    candidate_svc = CandidateService()
    manifesto_svc = ManifestoService()
    path = req.path.rstrip("/") or "/"

    try:
        if req.method == "GET" and path == "/health":
            return _response({"status": "ok"})

        if req.method == "POST" and path == "/booth/nearby":
            payload = NearbyRequest.model_validate(req.get_json(silent=True) or {})
            result = asyncio.run(
                geo.find_nearby_booths(
                    lat=payload.lat,
                    lng=payload.lng,
                    radius_km=payload.radius_km,
                )
            )
            return _response(result.model_dump())

        if req.method == "POST" and path == "/booth/directions":
            payload = DirectionsRequest.model_validate(req.get_json(silent=True) or {})
            result = asyncio.run(geo.get_directions(payload))
            return _response(result.model_dump())

        if req.method == "GET" and path.startswith("/booth/verify/"):
            epic_number = path.rsplit("/", maxsplit=1)[-1]
            result = asyncio.run(geo.verify_booth_assignment(epic_number))
            return _response(result.model_dump())

        if req.method == "POST" and path == "/candidate/search":
            payload = CandidateSearchRequest.model_validate(
                req.get_json(silent=True) or {},
            )
            if payload.constituency:
                result = asyncio.run(
                    candidate_svc.search_by_constituency(payload.constituency),
                )
            else:
                result = asyncio.run(
                    candidate_svc.search_by_location(payload.lat, payload.lng),
                )
            return _response(result.model_dump())

        if req.method == "GET" and path.startswith("/candidate/") and path.endswith("/background"):
            candidate_id = path.split("/")[2]
            result = asyncio.run(candidate_svc.background_check(candidate_id))
            return _response(result.model_dump())

        if req.method == "POST" and path == "/candidate/compare":
            payload = CompareRequest.model_validate(
                req.get_json(silent=True) or {},
            )
            result = asyncio.run(candidate_svc.compare(payload.candidate_ids))
            return _response(result.model_dump())

        if req.method == "POST" and path == "/manifesto/compare":
            payload = ManifestoCompareRequest.model_validate(
                req.get_json(silent=True) or {},
            )
            result = asyncio.run(
                manifesto_svc.compare_manifestos(
                    party_names=payload.party_names,
                    categories=payload.categories,
                    include_past_promises=payload.include_past_promises,
                )
            )
            return _response(result.model_dump())

    except ValidationError as error:
        return _response({"detail": error.errors()}, status=422)

    return _response({"detail": "Not found"}, status=404)


def _response(payload: dict[str, Any], status: int = 200) -> https_fn.Response:
    return https_fn.Response(
        json.dumps(payload),
        status=status,
        headers={
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Origin": "https://civiksutra-2604261729.web.app",
            "Content-Type": "application/json",
        },
    )
