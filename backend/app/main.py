from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import JSONResponse
import tempfile
import shutil
import os
import subprocess
import json

API_KEY = os.environ.get("API_KEY")

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}


def write_upload(tmpdir: str, upload: UploadFile, dest_name: str) -> str:
    dest = os.path.join(tmpdir, dest_name)
    with open(dest, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return dest

@app.post("/allocate")
async def allocate(courses: UploadFile = File(...), ras: UploadFile = File(...), x_api_key: str | None = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    tmpdir = tempfile.mkdtemp(prefix="ra-alloc-")
    try:
        courses_path = write_upload(tmpdir, courses, "courses.xlsx")
        ras_path = write_upload(tmpdir, ras, "ras.xlsx")
        slotmap_path = os.path.join(tmpdir, "l_to_slot_map.csv")
        theories = ['A1','F1','D1','TB1','TG1','B1','G1','E1','TC1','TAA1',
                    'C1','V1','V2','D1','TE1','TCC1','E1','TA1','TF1','TD1',
                    'A2','F2','D2','TB2','TG2','B2','G2','E2','TC2','TAA2',
                    'C2','TD2','TBB2','D2','TE2','TCC2','E2','TA2','TF2','TDD2']
        with open(slotmap_path, "w") as f:
            for i in range(1, 161):
                f.write(f"L{i},{theories[i % len(theories)]}\n")

        output_path = os.path.join(tmpdir, "allocations.json")
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "run_allocation.py")
        script_path = os.path.abspath(script_path)

        proc = subprocess.run(
            ["python", script_path, "--courses", courses_path, "--ras", ras_path, "--slotmap", slotmap_path, "--output", output_path],
            capture_output=True,
            text=True,
            check=False
        )
        if proc.returncode != 0:
            raise HTTPException(status_code=500, detail={"stdout": proc.stdout, "stderr": proc.stderr})

        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Output file missing")

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return JSONResponse(content=data)
    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass
