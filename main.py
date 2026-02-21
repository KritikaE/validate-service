import io
import csv
from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# ✅ CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Manual CORS header on every response
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# ✅ Handle preflight OPTIONS request
@app.options("/upload")
async def options_upload():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

# === CONSTANTS ===
VALID_TOKEN = "0ovhhx4k0b622ci1"
ALLOWED_EXTENSIONS = {".csv", ".json", ".txt"}
MAX_FILE_SIZE = 60 * 1024  # 60KB in bytes
YOUR_EMAIL = "24f2000844@ds.study.iitm.ac.in"  # ← Change this!

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_upload_token_5615: str = Header(None)
):
    # ─── Check the token ───────────────────────────────────────────
    if x_upload_token_5615 != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing token")

    # ─── Check file extension ──────────────────────────────────────
    filename = file.filename or ""
    dot_index = filename.rfind(".")
    extension = filename[dot_index:].lower() if dot_index != -1 else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Bad Request: File type not allowed")

    # ─── Read file contents & check size ───────────────────────────
    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Payload Too Large: File exceeds 60KB")

    # ─── Parse CSV and compute statistics ──────────────────────────
    if extension == ".csv":
        text = contents.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)

        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty")

        columns = list(rows[0].keys())
        total_value = 0.0
        category_counts = {}

        for row in rows:
            if "value" in row:
                try:
                    total_value += float(row["value"])
                except ValueError:
                    pass

            if "category" in row:
                cat = row["category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1

        return JSONResponse(
            content={
                "email": YOUR_EMAIL,
                "filename": filename,
                "rows": len(rows),
                "columns": columns,
                "totalValue": round(total_value, 2),
                "categoryCounts": category_counts,
            },
            headers={"Access-Control-Allow-Origin": "*"}
        )

    # For .json or .txt
    return JSONResponse(
        content={"email": YOUR_EMAIL, "filename": filename, "message": "File accepted"},
        headers={"Access-Control-Allow-Origin": "*"}
    )
