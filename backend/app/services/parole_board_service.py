from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import ApiError
from backend.app.models.parole_board import ParoleBoardOffice, ParoleBoardUnitMapping

DATASETS_DIR = Path(__file__).resolve().parents[3] / "datasets"
OFFICES_DATASET_PATH = DATASETS_DIR / "parole_board_offices.json"
UNIT_MAPPINGS_DATASET_PATH = DATASETS_DIR / "parole_board_unit_mappings.json"

UNIT_NAME_ALIASES = {
    "COLE": "COLE STATE JAIL",
    "BILL CLEMENTS": "CLEMENTS UNIT",
    "BILL CLEMENTS UNIT": "CLEMENTS UNIT",
    "LINDSEY SJ": "LINDSEY STATE JAIL",
}


def normalize_unit_name(unit_name: str) -> str:
    return re.sub(r"\s+", " ", unit_name.replace("*", " ")).strip().upper()


def _read_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def load_office_seed_rows() -> list[dict[str, Any]]:
    return _read_json(OFFICES_DATASET_PATH)


def load_unit_mapping_seed_rows() -> list[dict[str, Any]]:
    return _read_json(UNIT_MAPPINGS_DATASET_PATH)


def collapse_unit_mapping_rows() -> list[dict[str, Any]]:
    offices_by_code = {row["office_code"]: row for row in load_office_seed_rows()}
    grouped: dict[str, list[dict[str, Any]]] = {}

    for row in load_unit_mapping_seed_rows():
        normalized_unit_name = normalize_unit_name(row["unit_name"])
        candidate = {
            "unit_name": row["unit_name"],
            "normalized_unit_name": normalized_unit_name,
            "office_code": row["office_code"],
            "office_name": offices_by_code[row["office_code"]]["office_name"],
        }
        grouped.setdefault(normalized_unit_name, []).append(candidate)

    collapsed_rows: list[dict[str, Any]] = []
    for normalized_unit_name in sorted(grouped):
        candidates = grouped[normalized_unit_name]
        # TEMP_RULE: parole board routing rule placeholder
        # real TDCJ routing logic to be implemented later
        selected = sorted(candidates, key=lambda item: item["office_name"])[0]
        collapsed_rows.append(selected)
    return collapsed_rows


def load_seeded_unit_lookup() -> dict[str, dict[str, Any]]:
    offices_by_code = {row["office_code"]: row for row in load_office_seed_rows()}
    lookup: dict[str, dict[str, Any]] = {}
    for mapping in collapse_unit_mapping_rows():
        lookup[mapping["normalized_unit_name"]] = offices_by_code[mapping["office_code"]]
    return lookup


def resolve_seeded_office_for_unit(unit_name: str) -> Optional[dict[str, Any]]:
    if not unit_name:
        return None

    lookup = load_seeded_unit_lookup()
    for candidate_key in candidate_unit_lookup_keys(unit_name):
        office = lookup.get(candidate_key)
        if office is not None:
            return office
    return None


def candidate_unit_lookup_keys(unit_name: str) -> list[str]:
    normalized = normalize_unit_name(unit_name)
    alias = UNIT_NAME_ALIASES.get(normalized)
    candidates = [normalized]
    if alias:
        candidates.append(alias)
    if normalized.endswith(" UNIT"):
        candidates.append(normalized[: -len(" UNIT")].strip())
    else:
        candidates.append(f"{normalized} UNIT")
    if normalized.endswith(" SJ"):
        candidates.append(f"{normalized[: -len(' SJ')].strip()} STATE JAIL")
    else:
        candidates.append(f"{normalized} STATE JAIL")
    return list(dict.fromkeys(candidate for candidate in candidates if candidate))


def lookup_parole_board_office(unit_name: str, sid: Optional[str] = None) -> dict[str, Any]:
    normalized_unit = normalize_unit_name(unit_name)
    if not normalized_unit:
        raise ApiError(
            400,
            "validation_error",
            "Request validation failed.",
            details={"fields": ["unit"]},
        )

    office = resolve_seeded_office_for_unit(normalized_unit)
    if office is None:
        details: dict[str, Any] = {"unit": unit_name}
        if sid:
            details["sid"] = sid
        raise ApiError(
            404,
            "not_found",
            "No parole board office was found for that unit.",
            details=details,
        )

    address_lines = [office["address_line_1"]]
    if office.get("address_line_2"):
        address_lines.append(office["address_line_2"])

    return {
        "office_code": office["office_code"],
        "office_name": office["office_name"],
        "address_lines": address_lines,
        "city": office["city"],
        "state": office["state"],
        "postal_code": office["postal_code"],
        "phone": office.get("phone"),
        "notes": office.get("notes"),
    }


def seed_parole_board_reference_data(session: Session) -> tuple[int, int]:
    office_rows = load_office_seed_rows()
    mapping_rows = collapse_unit_mapping_rows()

    office_ids_by_code: dict[str, uuid.UUID] = {}
    offices_written = 0
    for row in office_rows:
        office = session.scalar(
            select(ParoleBoardOffice).where(ParoleBoardOffice.office_code == row["office_code"])
        )
        if office is None:
            office = ParoleBoardOffice(office_code=row["office_code"])
            session.add(office)
        office.office_name = row["office_name"]
        office.address_line_1 = row["address_line_1"]
        office.address_line_2 = row["address_line_2"]
        office.city = row["city"]
        office.state = row["state"]
        office.postal_code = row["postal_code"]
        office.phone = row["phone"]
        office.notes = row["notes"]
        session.flush()
        office_ids_by_code[row["office_code"]] = office.id
        offices_written += 1

    mappings_written = 0
    for row in mapping_rows:
        office_id = office_ids_by_code[row["office_code"]]
        mapping = session.scalar(
            select(ParoleBoardUnitMapping).where(ParoleBoardUnitMapping.unit_name == row["unit_name"])
        )
        if mapping is None:
            mapping = ParoleBoardUnitMapping(unit_name=row["unit_name"], office_id=office_id)
            session.add(mapping)
        else:
            mapping.office_id = office_id
        mappings_written += 1

    return offices_written, mappings_written
