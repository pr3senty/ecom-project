from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Iterable, Union


@dataclass(frozen=True)
class CsvParseError:
    row: Union[int, None]
    message: str


@dataclass(frozen=True)
class CsvParseResult:
    rows: list[tuple[int, dict[str, str]]]
    errors: list[CsvParseError]


def _normalize_header(value: str) -> str:
    return value.strip().lower()


def _normalize_text(value: Union[str, None]) -> str:
    return (value or "").strip()


def _detect_dialect(text: str) -> csv.Dialect:
    sample = text[:2048]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        return csv.excel


def _header_map(fieldnames: Union[Iterable[str], None]) -> dict[str, str]:
    if fieldnames is None:
        return {}
    return {_normalize_header(fieldname): fieldname for fieldname in fieldnames}


def parse_csv(content: bytes, expected_headers: Iterable[str]) -> CsvParseResult:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return CsvParseResult(
            rows=[],
            errors=[CsvParseError(None, "CSV file must be encoded as UTF-8")],
        )

    if not text.strip():
        return CsvParseResult(
            rows=[],
            errors=[CsvParseError(None, "CSV file is empty")],
        )

    reader = csv.DictReader(io.StringIO(text), dialect=_detect_dialect(text))
    headers = _header_map(reader.fieldnames)
    missing_headers = [
        header for header in expected_headers if _normalize_header(header) not in headers
    ]
    if missing_headers:
        return CsvParseResult(
            rows=[],
            errors=[
                CsvParseError(
                    None,
                    "Missing required CSV headers: " + ", ".join(missing_headers),
                )
            ],
        )

    rows: list[tuple[int, dict[str, str]]] = []
    errors: list[CsvParseError] = []

    for row_number, raw_row in enumerate(reader, start=2):
        if not any(
            _normalize_text(value)
            for key, value in raw_row.items()
            if key is not None and value
        ):
            continue

        if raw_row.get(None):
            errors.append(CsvParseError(row_number, "Row has too many columns"))
            continue

        row = {
            normalized_header: _normalize_text(raw_row.get(original_header))
            for normalized_header, original_header in headers.items()
        }
        rows.append((row_number, row))

    return CsvParseResult(rows=rows, errors=errors)
