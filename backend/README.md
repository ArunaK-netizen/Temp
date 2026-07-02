Python backend for RA allocation service

This service exposes a /allocate endpoint that accepts multipart form uploads:
- courses: Excel file (.xlsx)
- ras: Excel file (.xlsx)

The service runs the allocation script and returns JSON with fields:
- allocations: list
- unallocatedLabs: list

Environment variables:
- API_KEY: (optional) API key required via header `X-API-KEY`.

Run locally:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Test with curl:

```bash
curl -X POST "http://localhost:8000/allocate" \
  -H "X-API-KEY: your-key-here" \
  -F "courses=@/path/to/courses.xlsx" \
  -F "ras=@/path/to/ras.xlsx"
```
