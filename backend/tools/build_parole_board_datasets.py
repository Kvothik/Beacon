from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

BASE_URL = "https://www.tdcj.texas.gov/bpp/brd_locations/"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "datasets"
OFFICES = [
    ("AUSTIN", "AustinOffice.html", "Austin_units.htm"),
    ("AMARILLO", "AmarilloOffice.html", "Amarillo_units.htm"),
    ("ANGLETON", "AngletonOffice.html", "Angleton_units.htm"),
    ("GATESVILLE", "GatesvilleOffice.html", "Gatesville_units.htm"),
    ("HUNTSVILLE", "HuntsvilleOffice.html", "Huntsville_units.htm"),
    ("PALESTINE", "PalestineOffice.html", "Palestine_units.htm"),
    ("SAN_ANTONIO", "SanAntonioOffice.html", "SanAntonio_units.htm"),
]


def fetch(path: str) -> str:
    request = Request(BASE_URL + path, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "ignore")


def clean_lines(fragment: str) -> list[str]:
    fragment = unescape(fragment)
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"</p>", "\n", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    lines = [re.sub(r"\s+", " ", line).strip() for line in fragment.splitlines()]
    return [line for line in lines if line]


def parse_office(code: str, office_page: str) -> dict[str, object]:
    html = fetch(office_page)
    content = html.split("<h1", 1)[1].split("Updated", 1)[0]
    lines = clean_lines(content)
    office_name = " ".join(lines.pop(0).lstrip("> ").split()).title()
    address_line_1 = lines.pop(0)
    city_line = lines.pop(0)
    address_line_2 = None
    if not ("," in city_line and "TX" in city_line):
        address_line_2 = city_line
        city_line = lines.pop(0)
    match = re.match(r"(.+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$", city_line)
    if not match:
        raise ValueError(f"Unable to parse city/state/postal line for {code}: {city_line}")
    city, state, postal_code = match.groups()
    phone = None
    for line in lines:
        if "Board Member" in line or "Chair" in line or "See Assigned Units" in line:
            break
        if "Fax" in line:
            continue
        if line.lower().startswith("phone:"):
            phone = line.split(":", 1)[1].strip()
            break
        if re.search(r"\d{3}[-)]", line):
            phone = line
            break
    return {
        "office_code": code,
        "office_name": office_name,
        "address_line_1": address_line_1,
        "address_line_2": address_line_2,
        "city": city,
        "state": state,
        "postal_code": postal_code,
        "phone": phone,
        "notes": None,
    }


def parse_units(units_page: str, office_code: str) -> list[dict[str, str]]:
    html = fetch(units_page)
    content = html.split("<h1", 1)[1].split('<div id="bottom_panel">', 1)[0]
    mappings: list[dict[str, str]] = []
    for match in re.findall(r"<li>(.*?)</li>", content, flags=re.IGNORECASE | re.DOTALL):
        unit_name = " ".join(clean_lines(match)).replace("*", "").strip()
        if not unit_name:
            continue
        if "Board Office" in unit_name or unit_name in {
            "Austin Office",
            "Amarillo Office",
            "Angleton Office",
            "Gatesville Office",
            "Huntsville Office",
            "Palestine Office",
            "San Antonio Office",
        }:
            continue
        mappings.append({"unit_name": unit_name, "office_code": office_code})
    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in mappings:
        key = (row["unit_name"], row["office_code"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    offices = [parse_office(code, office_page) for code, office_page, _ in OFFICES]
    mappings = []
    for code, _, units_page in OFFICES:
        mappings.extend(parse_units(units_page, code))

    (OUTPUT_DIR / "parole_board_offices.json").write_text(json.dumps(offices, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "parole_board_unit_mappings.json").write_text(json.dumps(mappings, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(offices)} offices and {len(mappings)} raw unit mappings to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
