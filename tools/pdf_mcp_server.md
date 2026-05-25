# Local PDF MCP Server

This repository includes a minimal `stdio` MCP server for PDFs in `raw/`.

## Run

From the repository root:

```powershell
python tools/pdf_mcp_server.py --root raw
```

Smoke test without starting MCP mode:

```powershell
python tools/pdf_mcp_server.py --root raw --self-test
```

## Tools

- `list_pdfs`: list PDF files under `raw/`.
- `pdf_info`: return path, file size, and best-effort page count.
- `extract_text`: extract PDF text with optional `max_chars`.

## PDF Backends

The server tries these backends in order:

1. `PyMuPDF` (`pip install pymupdf`)
2. `pypdf` (`pip install pypdf`)
3. `pdftotext` from Poppler
4. built-in best-effort fallback

For research papers, install `PyMuPDF` if possible. The fallback is dependency-free but cannot reliably decode all embedded fonts or scanned PDFs.

## MCP Client Config Example

Use an absolute path for `cwd`:

```json
{
  "mcpServers": {
    "pdf": {
      "command": "python",
      "args": ["tools/pdf_mcp_server.py", "--root", "raw"],
      "cwd": "E:/drone_rf_identification/drone-RF-identification"
    }
  }
}
```

The server restricts access to the configured `--root` and only accepts `.pdf` paths.
