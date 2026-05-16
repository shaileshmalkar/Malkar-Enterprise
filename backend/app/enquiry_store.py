import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

BACKEND_ROOT = Path(__file__).resolve().parent.parent
ENQUIRIES_DIR = BACKEND_ROOT / "data" / "enquiries"
JSON_PATH = ENQUIRIES_DIR / "enquiries.json"
CSV_PATH = ENQUIRIES_DIR / "enquiries.csv"

CSV_HEADERS = ("id", "submitted_at", "name", "mobile", "email", "message")


def _load_json_entries() -> list[dict]:
    if not JSON_PATH.is_file():
        return []
    try:
        data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _normalize(payload: dict) -> dict:
    name = str(payload.get("name", "")).strip()
    mobile = str(payload.get("mobile", "")).strip()
    if not name:
        raise ValueError("Name is required")
    if not mobile:
        raise ValueError("Mobile number is required")

    return {
        "id": str(uuid4()),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "mobile": mobile,
        "email": str(payload.get("email", "")).strip(),
        "message": str(payload.get("message", "")).strip(),
    }


def save_enquiry(payload: dict) -> dict:
    """Append enquiry to enquiries.json and enquiries.csv."""
    record = _normalize(payload)
    ENQUIRIES_DIR.mkdir(parents=True, exist_ok=True)

    entries = _load_json_entries()
    entries.append(record)
    JSON_PATH.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    write_header = not CSV_PATH.is_file() or CSV_PATH.stat().st_size == 0
    with CSV_PATH.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADERS)
        if write_header:
            writer.writeheader()
        writer.writerow({key: record[key] for key in CSV_HEADERS})

    return record


def enquiries_data_dir() -> str:
    return str(ENQUIRIES_DIR.resolve())
