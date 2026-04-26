from __future__ import annotations

import pytest

from src.services.scraper_service import ScraperService, _TableParser


SAMPLE_HTML = """
<html><body>
<table>
<tr><th>SNo</th><th>Name</th><th>Party</th><th>Criminal Cases</th><th>Education</th><th>Total Assets</th><th>Liabilities</th></tr>
<tr><td>1</td><td>Ramesh Kumar</td><td>BJP</td><td>0</td><td>MBA</td><td>2,10,00,000</td><td>30,00,000</td></tr>
<tr><td>2</td><td>Priya Singh</td><td>INC</td><td>1</td><td>LLB</td><td>8,50,00,000</td><td>1,20,00,000</td></tr>
<tr><td>3</td><td>Amit Verma</td><td>AAP</td><td>0</td><td>B.Tech</td><td>1,50,00,000</td><td>20,00,000</td></tr>
</table>
</body></html>
"""

MINIMAL_HTML = """
<html><body>
<table>
<tr><th>SNo</th><th>Name</th><th>Party</th></tr>
<tr><td>1</td><td>Candidate A</td><td>IND</td></tr>
</table>
</body></html>
"""

EMPTY_HTML = "<html><body><p>No data</p></body></html>"
MALFORMED_HTML = "<html><body><table><tr><td>broken"


def test_table_parser_extracts_rows() -> None:
    parser = _TableParser()
    parser.feed(SAMPLE_HTML)

    assert len(parser.rows) == 4
    assert parser.rows[0][1] == "Name"
    assert parser.rows[1][1] == "Ramesh Kumar"


def test_myneta_parses_candidate_table() -> None:
    service = ScraperService()
    candidates = service._parse_candidate_table(SAMPLE_HTML, "Test")

    assert len(candidates) == 3
    assert candidates[0].name == "Ramesh Kumar"
    assert candidates[0].party == "BJP"
    assert candidates[0].criminal_cases == 0
    assert candidates[0].education == "MBA"
    assert candidates[1].name == "Priya Singh"
    assert candidates[1].criminal_cases == 1


def test_myneta_handles_missing_fields() -> None:
    service = ScraperService()
    candidates = service._parse_candidate_table(MINIMAL_HTML, "Test")

    assert len(candidates) == 0


def test_myneta_fallback_on_structure_change() -> None:
    service = ScraperService()
    candidates = service._parse_candidate_table(EMPTY_HTML, "Test")

    assert candidates == []


def test_malformed_html_does_not_crash() -> None:
    service = ScraperService()
    candidates = service._parse_candidate_table(MALFORMED_HTML, "Test")

    assert isinstance(candidates, list)


@pytest.mark.asyncio
async def test_affidavit_returns_none_when_unavailable() -> None:
    service = ScraperService()
    result = await service.fetch_eci_affidavit("nonexistent_candidate")

    assert result is None


def test_constituency_slug() -> None:
    assert ScraperService._constituency_slug("South Delhi") == "south-delhi"
    assert ScraperService._constituency_slug("New Delhi") == "new-delhi"
    assert ScraperService._constituency_slug("  MUMBAI North  ") == "mumbai-north"


def test_parse_currency_crore() -> None:
    assert ScraperService._parse_currency("2.1 Crore") == 21_000_000


def test_parse_currency_lakh() -> None:
    assert ScraperService._parse_currency("5 Lakh") == 500_000


def test_parse_currency_plain() -> None:
    assert ScraperService._parse_currency("2,10,00,000") == 21_000_000


def test_parse_currency_empty() -> None:
    assert ScraperService._parse_currency("") == 0
    assert ScraperService._parse_currency("N/A") == 0


def test_parse_int_with_noise() -> None:
    assert ScraperService._parse_int("3 cases") == 3
    assert ScraperService._parse_int("0") == 0
    assert ScraperService._parse_int("None") == 0
