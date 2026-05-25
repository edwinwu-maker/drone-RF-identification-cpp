#!/usr/bin/env python3
"""Minimal stdio MCP server for reading local PDFs.

The server intentionally avoids the MCP SDK so it can run in small research
repositories. PDF extraction uses optional local backends when available.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zlib
from pathlib import Path
from typing import Any


SERVER_NAME = "local-pdf-mcp"
SERVER_VERSION = "0.1.0"


def _json_response(request_id: Any, result: Any = None, error: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error is None:
        payload["result"] = result
    else:
        payload["error"] = error
    return payload


def _write(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    sys.stdout.flush()


def _safe_path(root: Path, requested: str | None) -> Path:
    if not requested:
        raise ValueError("Missing path")
    candidate = Path(requested)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    if root not in candidate.parents and candidate != root:
        raise ValueError(f"Path is outside root: {requested}")
    if candidate.suffix.lower() != ".pdf":
        raise ValueError(f"Path is not a PDF: {requested}")
    if not candidate.exists():
        raise FileNotFoundError(str(candidate))
    return candidate


def list_pdfs(root: Path) -> list[dict[str, Any]]:
    files = []
    for path in sorted(root.rglob("*.pdf")):
        stat = path.stat()
        files.append(
            {
                "path": str(path.relative_to(root)),
                "name": path.name,
                "size_bytes": stat.st_size,
            }
        )
    return files


def pdf_info(root: Path, path_text: str) -> dict[str, Any]:
    path = _safe_path(root, path_text)
    stat = path.stat()
    info = {
        "path": str(path.relative_to(root)),
        "name": path.name,
        "size_bytes": stat.st_size,
        "backend": "basic",
    }
    page_count = _page_count_basic(path)
    if page_count is not None:
        info["pages"] = page_count
    return info


def _page_count_basic(path: Path) -> int | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    matches = re.findall(rb"/Type\s*/Page\b", data)
    return len(matches) if matches else None


def extract_text(root: Path, path_text: str, max_chars: int = 20000) -> dict[str, Any]:
    path = _safe_path(root, path_text)
    max_chars = max(1000, min(int(max_chars or 20000), 200000))

    extractors = (
        _extract_with_pymupdf,
        _extract_with_pypdf,
        _extract_with_pdftotext,
        _extract_basic,
    )
    errors: list[str] = []
    for extractor in extractors:
        try:
            text, backend = extractor(path)
        except Exception as exc:  # noqa: BLE001 - report backend failures to MCP caller.
            errors.append(f"{extractor.__name__}: {exc}")
            continue
        cleaned = _clean_text(text)
        if cleaned:
            truncated = len(cleaned) > max_chars
            return {
                "path": str(path.relative_to(root)),
                "backend": backend,
                "text": cleaned[:max_chars],
                "chars": min(len(cleaned), max_chars),
                "truncated": truncated,
                "errors": errors,
            }
        errors.append(f"{extractor.__name__}: no text extracted")

    raise RuntimeError(
        "No PDF text backend succeeded. Install one of: PyMuPDF (`pip install pymupdf`), "
        "pypdf (`pip install pypdf`), or poppler `pdftotext`. Details: "
        + " | ".join(errors)
    )


def _extract_with_pymupdf(path: Path) -> tuple[str, str]:
    import fitz  # type: ignore[import-not-found]

    parts = []
    with fitz.open(path) as doc:
        for index, page in enumerate(doc, start=1):
            parts.append(f"\n\n--- page {index} ---\n")
            parts.append(page.get_text())
    return "".join(parts), "pymupdf"


def _extract_with_pypdf(path: Path) -> tuple[str, str]:
    from pypdf import PdfReader  # type: ignore[import-not-found]

    reader = PdfReader(str(path))
    parts = []
    for index, page in enumerate(reader.pages, start=1):
        parts.append(f"\n\n--- page {index} ---\n")
        parts.append(page.extract_text() or "")
    return "".join(parts), "pypdf"


def _extract_with_pdftotext(path: Path) -> tuple[str, str]:
    proc = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.stdout, "pdftotext"


def _extract_basic(path: Path) -> tuple[str, str]:
    """Best-effort dependency-free extraction for simple text PDFs."""

    data = path.read_bytes()
    chunks: list[bytes] = []
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, flags=re.S):
        raw = match.group(1)
        for candidate in (raw, raw.strip()):
            try:
                chunks.append(zlib.decompress(candidate))
                break
            except zlib.error:
                continue
    decoded = b"\n".join(chunks).decode("latin-1", errors="ignore")

    strings: list[str] = []
    for literal in re.findall(r"\((?:\\.|[^\\)])*\)", decoded):
        strings.append(_decode_pdf_literal(literal[1:-1]))
    for hex_text in re.findall(r"<([0-9A-Fa-f\s]{4,})>", decoded):
        cleaned = re.sub(r"\s+", "", hex_text)
        try:
            raw = bytes.fromhex(cleaned)
        except ValueError:
            continue
        strings.append(raw.decode("utf-16-be", errors="ignore") or raw.decode("latin-1", errors="ignore"))
    return "\n".join(s for s in strings if s.strip()), "basic"


def _decode_pdf_literal(value: str) -> str:
    value = value.replace(r"\(", "(").replace(r"\)", ")").replace(r"\\", "\\")
    value = value.replace(r"\n", "\n").replace(r"\r", "\r").replace(r"\t", "\t")
    return value


def _clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def _tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "list_pdfs",
            "description": "List PDF files under the configured root directory.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "pdf_info",
            "description": "Return basic metadata for a PDF under the configured root directory.",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            },
        },
        {
            "name": "extract_text",
            "description": "Extract text from a PDF under the configured root directory.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "max_chars": {"type": "integer", "minimum": 1000, "maximum": 200000},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    ]


def _content(value: Any) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(value, ensure_ascii=True, indent=2),
            }
        ]
    }


def _handle(root: Path, request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params") or {}

    try:
        if method == "initialize":
            return _json_response(
                request_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                },
            )
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return _json_response(request_id, {"tools": _tools()})
        if method == "tools/call":
            name = params.get("name")
            args = params.get("arguments") or {}
            if name == "list_pdfs":
                return _json_response(request_id, _content(list_pdfs(root)))
            if name == "pdf_info":
                return _json_response(request_id, _content(pdf_info(root, args.get("path"))))
            if name == "extract_text":
                return _json_response(
                    request_id,
                    _content(extract_text(root, args.get("path"), args.get("max_chars", 20000))),
                )
            raise ValueError(f"Unknown tool: {name}")
        return _json_response(request_id, error={"code": -32601, "message": f"Unknown method: {method}"})
    except Exception as exc:  # noqa: BLE001 - MCP errors must be serialized.
        return _json_response(request_id, error={"code": -32000, "message": str(exc)})


def _self_test(root: Path) -> None:
    print(json.dumps({"pdfs": list_pdfs(root)}, ensure_ascii=True, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Local PDF MCP stdio server")
    parser.add_argument("--root", default="raw", help="Root directory containing PDFs")
    parser.add_argument("--self-test", action="store_true", help="List PDFs and exit")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Root is not a directory: {root}")

    if args.self_test:
        _self_test(root)
        return 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = _handle(root, request)
        except json.JSONDecodeError as exc:
            response = _json_response(None, error={"code": -32700, "message": str(exc)})
        if response is not None:
            _write(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
