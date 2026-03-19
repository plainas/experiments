#!/usr/bin/env python3
"""Minimal XML -> JSON CLI wrapper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import xmltodict


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert XML file to JSON.")
    parser.add_argument("xml_path", help="Path to the XML file to convert.")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output with indentation.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    xml_file = Path(args.xml_path)
    if not xml_file.exists():
        print(f"error: file not found: {xml_file}", file=sys.stderr)
        return 2

    try:
        xml_text = xml_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: failed to read {xml_file}: {exc}", file=sys.stderr)
        return 2

    try:
        data = xmltodict.parse(xml_text)
    except Exception as exc:  # pragma: no cover - xmltodict raises generic exceptions
        print(f"error: failed to parse XML: {exc}", file=sys.stderr)
        return 1

    indent = 2 if args.pretty else None
    json_output = json.dumps(data, ensure_ascii=False, indent=indent)
    print(json_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
