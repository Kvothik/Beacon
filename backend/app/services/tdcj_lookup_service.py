from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from time import sleep
from typing import Any, Optional
from urllib.parse import parse_qs, urlencode, urljoin, urlparse
from urllib.request import Request as UrlRequest, urlopen

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

from backend.app.core.security import ApiError

TDCJ_BASE_URL = "https://inmate.tdcj.texas.gov"
TDCJ_SEARCH_URL = f"{TDCJ_BASE_URL}/InmateSearch/search.action"
TDCJ_DETAIL_URL = f"{TDCJ_BASE_URL}/InmateSearch/viewDetail.action"
TDCJ_SOURCE = "Texas Department of Criminal Justice"
TDCJ_SOURCE_NOTE = (
    "Information provided is updated once daily during weekdays and may not reflect the true current "
    "status or location."
)


@dataclass(frozen=True)
class SearchRequest:
    last_name: Optional[str] = None
    first_name_initial: Optional[str] = None
    tdcj_number: Optional[str] = None
    sid: Optional[str] = None
    page: int = 1


@dataclass(frozen=True)
class PaginationState:
    current_page: int
    total_pages: int
    has_more: bool
    last_search: Optional[str] = None


class TdcjLookupService:
    def __init__(
        self,
        *,
        timeout_seconds: float = 15.0,
        throttle_seconds: float = 0.5,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._throttle_seconds = throttle_seconds
        self._transport = transport

    def search_offenders(self, request: SearchRequest) -> dict[str, Any]:
        self._validate_search_request(request)
        response_text = self._post_search(request)
        parsed = self.parse_search_results_page(response_text)

        pagination = parsed["pagination"]
        requested_page = max(request.page, 1)
        if requested_page > 1:
            if not pagination["last_search"]:
                raise ApiError(
                    502,
                    "tdcj_parser_error",
                    "Offender lookup results could not be parsed.",
                    details={"reason": "missing_pagination_form"},
                    retryable=False,
                )
            if requested_page > pagination["total_pages"]:
                parsed["results"] = []
                parsed["pagination"] = {
                    "current_page": requested_page,
                    "total_pages": pagination["total_pages"],
                    "has_more": False,
                }
                parsed["retrieved_at"] = _iso_utc_now()
                return parsed
            response_text = self._post_paginated_search(
                last_search=pagination["last_search"],
                current_page=requested_page,
                total_page_count=pagination["total_pages"],
            )
            parsed = self.parse_search_results_page(response_text)

        return {
            "results": parsed["results"],
            "pagination": {
                "current_page": parsed["pagination"]["current_page"],
                "total_pages": parsed["pagination"]["total_pages"],
                "has_more": parsed["pagination"]["has_more"],
            },
            "source": TDCJ_SOURCE,
            "retrieved_at": _iso_utc_now(),
        }

    def get_offender_detail(self, sid: str) -> dict[str, Any]:
        normalized_sid = sid.strip()
        if not normalized_sid:
            raise ApiError(400, "tdcj_invalid_sid", "A valid SID is required.")

        html = self._get_detail_page(normalized_sid)
        parsed = self.parse_detail_page(html)
        parsed["source"] = TDCJ_SOURCE
        parsed["retrieved_at"] = _iso_utc_now()
        parsed["source_note"] = TDCJ_SOURCE_NOTE
        return parsed

    def _post_search(self, request: SearchRequest) -> str:
        payload = {
            "page": "index",
            "lastName": (request.last_name or "").strip(),
            "firstName": (request.first_name_initial or "").strip()[:1],
            "tdcj": (request.tdcj_number or "").strip(),
            "sid": (request.sid or "").strip(),
            "gender": "ALL",
            "race": "ALL",
            "btnSearch": "Search",
        }
        return self._request_with_retry("POST", TDCJ_SEARCH_URL, data=payload)

    def _post_paginated_search(
        self,
        *,
        last_search: str,
        current_page: int,
        total_page_count: int,
    ) -> str:
        payload = {
            "lastSearch": last_search,
            "currentPage": str(current_page),
            "totalPageCount": str(total_page_count),
        }
        return self._request_with_retry("POST", TDCJ_SEARCH_URL, data=payload)

    def _get_detail_page(self, sid: str) -> str:
        return self._request_with_retry("GET", TDCJ_DETAIL_URL, params={"sid": sid})

    def _request_with_retry(self, method: str, url: str, **kwargs: Any) -> str:
        headers = {"User-Agent": "Beacon/0.1 (+https://github.com/openclaw/openclaw)"}
        last_exception: Exception | None = None
        for attempt in range(2):
            try:
                with httpx.Client(
                    timeout=self._timeout_seconds,
                    follow_redirects=True,
                    transport=self._transport,
                    headers=headers,
                ) as client:
                    response = client.request(method, url, **kwargs)
                    response.raise_for_status()
                    self._throttle()
                    return response.text
            except httpx.RemoteProtocolError as exc:
                last_exception = exc
                try:
                    response_text = self._request_with_urllib(method, url, headers=headers, **kwargs)
                    self._throttle()
                    return response_text
                except Exception as fallback_exc:
                    last_exception = fallback_exc
                    if attempt == 0:
                        sleep(0.5)
                        continue
                    raise ApiError(
                        502,
                        "tdcj_network_error",
                        "Offender lookup is temporarily unavailable.",
                        retryable=True,
                    ) from fallback_exc
            except httpx.HTTPStatusError as exc:
                last_exception = exc
                if exc.response.status_code == 404 and method == "GET":
                    raise ApiError(404, "tdcj_invalid_sid", "No offender was found for that SID.") from exc
            except httpx.HTTPError as exc:
                last_exception = exc
                if attempt == 0:
                    sleep(0.5)
                    continue
                raise ApiError(
                    502,
                    "tdcj_network_error",
                    "Offender lookup is temporarily unavailable.",
                    retryable=True,
                ) from exc

        raise ApiError(
            502,
            "tdcj_unavailable",
            "Offender lookup is temporarily unavailable.",
            retryable=True,
            details={"reason": type(last_exception).__name__ if last_exception else "unknown"},
        )

    def _request_with_urllib(self, method: str, url: str, *, headers: dict[str, str], **kwargs: Any) -> str:
        params = kwargs.get("params") or None
        data = kwargs.get("data") or None
        request_url = url
        if params:
            query = urlencode(params)
            separator = "&" if "?" in request_url else "?"
            request_url = f"{request_url}{separator}{query}"

        encoded_data = urlencode(data).encode("utf-8") if data else None
        request = UrlRequest(request_url, data=encoded_data, headers=headers, method=method.upper())
        with urlopen(request, timeout=self._timeout_seconds) as response:
            return response.read().decode("utf-8", errors="replace")

    def parse_search_results_page(self, html: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        self._assert_search_page(soup)

        table = soup.select_one("table.tdcj_table")
        if table is None:
            if self._looks_like_no_results_page(soup):
                pagination = self._parse_pagination(soup)
                return {
                    "results": [],
                    "pagination": {
                        "current_page": pagination.current_page,
                        "total_pages": pagination.total_pages,
                        "has_more": pagination.has_more,
                        "last_search": pagination.last_search,
                    },
                }
            raise self._parser_error("missing_results_table")

        tbody = table.find("tbody")
        if tbody is None:
            raise self._parser_error("missing_results_tbody")

        results: list[dict[str, Any]] = []
        for row in tbody.find_all("tr", recursive=False):
            normalized_row = self._parse_search_result_row(row)
            if normalized_row is not None:
                results.append(normalized_row)

        pagination = self._parse_pagination(soup)
        return {
            "results": results,
            "pagination": {
                "current_page": pagination.current_page,
                "total_pages": pagination.total_pages,
                "has_more": pagination.has_more,
                "last_search": pagination.last_search,
            },
        }

    def parse_detail_page(self, html: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        self._assert_detail_page(soup)

        values_by_label = self._extract_detail_labels(soup)
        sid_value = values_by_label.get("SID Number")
        if not sid_value:
            raise self._parser_error("missing_sid_number")

        visitation_raw = values_by_label.get("Inmate Visitation Eligible")
        return {
            "sid": sid_value,
            "tdcj_number": values_by_label.get("TDCJ Number"),
            "name": values_by_label.get("Name"),
            "race": values_by_label.get("Race"),
            "gender": values_by_label.get("Gender"),
            "age": _parse_int(values_by_label.get("Age")),
            "maximum_sentence_date": values_by_label.get("Maximum Sentence Date"),
            "current_facility": values_by_label.get("Current Facility"),
            "projected_release_date": values_by_label.get("Projected Release Date"),
            "parole_eligibility_date": values_by_label.get("Parole Eligibility Date"),
            "visitation_eligible": _normalize_yes_no(visitation_raw),
            "visitation_eligible_raw": visitation_raw,
            "scheduled_release_date_text": values_by_label.get("Scheduled Release Date"),
            "scheduled_release_type_text": values_by_label.get("Scheduled Release Type"),
            "scheduled_release_location_text": values_by_label.get("Scheduled Release Location"),
            "parole_review_url": self._extract_parole_review_url(soup),
            "offense_history": self._parse_offense_history(soup),
        }

    def _validate_search_request(self, request: SearchRequest) -> None:
        has_name_search = bool((request.last_name or "").strip()) and bool(
            (request.first_name_initial or "").strip()
        )
        has_tdcj_search = bool((request.tdcj_number or "").strip())
        has_sid_search = bool((request.sid or "").strip())
        if not any((has_name_search, has_tdcj_search, has_sid_search)):
            raise ApiError(
                400,
                "invalid_search_request",
                "Provide last name and first initial, TDCJ number, or SID.",
                details={"fields": ["last_name", "first_name_initial", "tdcj_number", "sid"]},
            )

    def _assert_search_page(self, soup: BeautifulSoup) -> None:
        title = _clean_text(soup.title.get_text(" ", strip=True) if soup.title else None)
        h1 = _clean_text(soup.find("h1").get_text(" ", strip=True) if soup.find("h1") else None)
        if title and "Search Result Listing" in title:
            return
        if h1 and "Inmate Information Search Result" in h1:
            return
        if self._looks_like_no_results_page(soup):
            return
        raise self._parser_error("unexpected_search_page")

    def _assert_detail_page(self, soup: BeautifulSoup) -> None:
        title = _clean_text(soup.title.get_text(" ", strip=True) if soup.title else None)
        h1 = _clean_text(soup.find("h1").get_text(" ", strip=True) if soup.find("h1") else None)
        if title and "Inmate Details" in title:
            return
        if h1 and "Inmate Information Details" in h1:
            return
        raise self._parser_error("unexpected_detail_page")

    def _looks_like_no_results_page(self, soup: BeautifulSoup) -> bool:
        text = soup.get_text(" ", strip=True)
        return "No records found" in text or "0 records found" in text or "No offender found" in text

    def _parse_search_result_row(self, row: Tag) -> Optional[dict[str, Any]]:
        header_cell = row.find("th")
        data_cells = row.find_all("td", recursive=False)
        if header_cell is None or len(data_cells) < 6:
            return None

        anchor = header_cell.select_one("a")
        if anchor is None:
            return None

        href = anchor.get("href")
        sid = _extract_sid_from_href(href)
        if not sid:
            raise self._parser_error("missing_sid_in_result_row")

        return {
            "name": _clean_text(anchor.get_text(" ", strip=True)),
            "sid": sid,
            "tdcj_number": _clean_text(data_cells[0].get_text(" ", strip=True)),
            "race": _clean_text(data_cells[1].get_text(" ", strip=True)),
            "gender": _clean_text(data_cells[2].get_text(" ", strip=True)),
            "projected_release_date": _clean_text(data_cells[3].get_text(" ", strip=True)),
            "unit": _clean_text(data_cells[4].get_text(" ", strip=True)),
            "age": _parse_int(data_cells[5].get_text(" ", strip=True)),
            "detail_url": urljoin(TDCJ_BASE_URL, href),
        }

    def _parse_pagination(self, soup: BeautifulSoup) -> PaginationState:
        form = soup.select_one("form#form_paginate")
        if form is None:
            return PaginationState(current_page=1, total_pages=1, has_more=False, last_search=None)

        current_page = _parse_int(_input_value(form, "currentPage")) or 1
        total_pages = _parse_int(_input_value(form, "totalPageCount")) or 1
        last_search = _input_value(form, "lastSearch")
        return PaginationState(
            current_page=current_page,
            total_pages=total_pages,
            has_more=current_page < total_pages,
            last_search=last_search,
        )

    def _extract_detail_labels(self, soup: BeautifulSoup) -> dict[str, str]:
        values: dict[str, str] = {}
        label_tags = soup.find_all(["th", "td", "span", "strong", "b", "font"])
        for tag in label_tags:
            label_text = _clean_label(tag.get_text(" ", strip=True))
            if label_text not in _DETAIL_LABELS:
                continue

            value = self._extract_value_for_label(tag)
            if value is not None:
                values[label_text] = value
        return values

    def _extract_value_for_label(self, tag: Tag) -> Optional[str]:
        inline_parts: list[str] = []
        for sibling in tag.next_siblings:
            if isinstance(sibling, str):
                text = _clean_text(sibling)
                if text:
                    inline_parts.append(text)
                continue

            if not isinstance(sibling, Tag):
                continue

            if sibling.name == "br":
                break

            text = _clean_text(sibling.get_text(" ", strip=True))
            if text:
                inline_parts.append(text)

        inline_value = _clean_text(" ".join(inline_parts))
        if inline_value:
            return inline_value

        next_sibling = tag.find_next_sibling()
        while next_sibling is not None:
            text = _clean_text(next_sibling.get_text(" ", strip=True))
            if text:
                return text
            next_sibling = next_sibling.find_next_sibling()

        parent_row = tag.find_parent("tr")
        if parent_row is not None:
            cells = parent_row.find_all(["th", "td"], recursive=False)
            if len(cells) >= 2:
                tag_index = cells.index(tag) if tag in cells else 0
                for cell in cells[tag_index + 1 :]:
                    text = _clean_text(cell.get_text(" ", strip=True))
                    if text:
                        return text

        parent = tag.parent if isinstance(tag.parent, Tag) else None
        if parent is not None:
            combined = [_clean_text(part) for part in parent.stripped_strings]
            combined = [part for part in combined if part]
            label_text = _clean_label(tag.get_text(" ", strip=True))
            if combined and combined[0].rstrip(":") == label_text:
                remaining = " ".join(combined[1:]).strip()
                return remaining or None
        return None

    def _extract_parole_review_url(self, soup: BeautifulSoup) -> Optional[str]:
        for anchor in soup.find_all("a"):
            if _clean_text(anchor.get_text(" ", strip=True)) == "Parole Review Information":
                href = anchor.get("href")
                return urljoin(TDCJ_BASE_URL, href) if href else None
        return None

    def _parse_offense_history(self, soup: BeautifulSoup) -> list[dict[str, Optional[str]]]:
        heading = soup.find(string=lambda value: isinstance(value, str) and "Offense History" in value)
        if heading is None:
            return []

        heading_tag = heading.parent if isinstance(heading.parent, Tag) else None
        if heading_tag is None:
            return []

        table = heading_tag.find_next("table")
        if table is None:
            return []

        body = table.find("tbody") or table
        offense_rows: list[dict[str, Optional[str]]] = []
        for row in body.find_all("tr"):
            header = row.find("th")
            cells = row.find_all("td", recursive=False)
            if header is None or len(cells) < 5:
                continue
            offense_rows.append(
                {
                    "offense_date": _clean_text(header.get_text(" ", strip=True)),
                    "offense": _clean_text(cells[0].get_text(" ", strip=True)),
                    "sentence_date": _clean_text(cells[1].get_text(" ", strip=True)),
                    "county": _clean_text(cells[2].get_text(" ", strip=True)),
                    "case_number": _clean_text(cells[3].get_text(" ", strip=True)),
                    "sentence_length": _clean_text(cells[4].get_text(" ", strip=True)),
                }
            )
        return offense_rows

    def _parser_error(self, reason: str) -> ApiError:
        return ApiError(
            502,
            "tdcj_parser_error",
            "Offender lookup results could not be parsed.",
            details={"reason": reason},
            retryable=False,
        )

    def _throttle(self) -> None:
        if self._throttle_seconds > 0:
            sleep(self._throttle_seconds)


_DETAIL_LABELS = {
    "SID Number",
    "TDCJ Number",
    "Name",
    "Race",
    "Gender",
    "Age",
    "Maximum Sentence Date",
    "Current Facility",
    "Projected Release Date",
    "Parole Eligibility Date",
    "Inmate Visitation Eligible",
    "Scheduled Release Date",
    "Scheduled Release Type",
    "Scheduled Release Location",
}


def _extract_sid_from_href(href: Optional[str]) -> Optional[str]:
    if not href:
        return None
    parsed = urlparse(href)
    values = parse_qs(parsed.query).get("sid")
    return values[0].strip() if values and values[0].strip() else None


def _input_value(form: Tag, name: str) -> Optional[str]:
    field = form.find("input", attrs={"name": name})
    if field is None:
        return None
    return _clean_text(field.get("value"))


def _clean_label(value: Optional[str]) -> Optional[str]:
    text = _clean_text(value)
    return text[:-1] if text and text.endswith(":") else text


def _clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    collapsed = value.replace("\xa0", " ").replace("</c:out>", " ")
    collapsed = " ".join(collapsed.split()).strip()
    if not collapsed:
        return None
    if collapsed.upper() == "NOT AVAILABLE":
        return None
    return collapsed


def _parse_int(value: Optional[str]) -> Optional[int]:
    text = _clean_text(value)
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _normalize_yes_no(value: Optional[str]) -> Optional[bool]:
    text = _clean_text(value)
    if text is None:
        return None
    normalized = text.upper()
    if normalized == "YES":
        return True
    if normalized == "NO":
        return False
    return None


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
