import io
import csv
from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS: Allow POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# === CONSTANTS ===
VALID_TOKEN = "0ovhhx4k0b622ci1"
ALLOWED_EXTENSIONS = {".csv", ".json", ".txt"}
MAX_FILE_SIZE = 60 * 1024  # 60KB in bytes
YOUR_EMAIL = "your-email@ds.study.iitm.ac.in"  # ← Change this!

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_upload_token_5615: str = Header(None)  # FastAPI auto-maps header name
):

    # ─── STEP 1: Check the token ───────────────────────────────────────────
    if x_upload_token_5615 != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing token")

    # ─── STEP 2: Check file extension ──────────────────────────────────────
    filename = file.filename or ""
    # Get the part after the last dot, e.g. "data.csv" → ".csv"
    dot_index = filename.rfind(".")
    extension = filename[dot_index:].lower() if dot_index != -1 else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Bad Request: File type not allowed")

    # ─── STEP 3: Read file contents & check size ───────────────────────────
    contents = await file.read()  # reads the raw bytes

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Payload Too Large: File exceeds 60KB")

    # ─── STEP 4: Parse CSV and compute statistics ──────────────────────────
    if extension == ".csv":
        text = contents.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))  # reads CSV into dicts
        rows = list(reader)

        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty")

        columns = list(rows[0].keys())          # column names from first row
        total_value = 0.0
        category_counts = {}

        for row in rows:
            # Add up the "value" column (convert string → float)
            if "value" in row:
                try:
                    total_value += float(row["value"])
                except ValueError:
                    pass  # skip bad values

            # Count each category
            if "category" in row:
                cat = row["category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "email": YOUR_EMAIL,
            "filename": filename,
            "rows": len(rows),
            "columns": columns,
            "totalValue": round(total_value, 2),
            "categoryCounts": category_counts,
        }

    # For .json or .txt files (non-CSV), just confirm success
    return {"email": YOUR_EMAIL, "filename": filename, "message": "File accepted"}
