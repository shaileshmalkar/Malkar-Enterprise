from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.enquiry_store import enquiries_data_dir, save_enquiry
from app.project_loader import DATA_ROOT, load_project_assets

app = FastAPI(title="Malkar Enterprises API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_CATEGORIES = [
    {"title": "Premium Retail", "subtitle": "High-street & mall formats", "image": "/images/cat-retail.jpg"},
    {"title": "Modern Office", "subtitle": "Grade-A commercial spaces", "image": "/images/cat-office.jpg"},
    {"title": "Smart Infrastructure", "subtitle": "Integrated utilities & services", "image": "/images/cat-infra.jpg"},
    {"title": "Sustainable Development", "subtitle": "Green-certified planning", "image": "/images/cat-green.jpg"},
]

CONSTRUCTION_PHASES = [
    {"id": "planning", "label": "Planning", "status": "done"},
    {"id": "foundation", "label": "Foundation", "status": "pending"},
    {"id": "structure", "label": "Structure", "status": "active"},
    {"id": "interior", "label": "Interior", "status": "pending"},
    {"id": "completion", "label": "Completion", "status": "pending"},
]

FLOORS = [
    "Basement", "Ground", "1st Floor", "2nd Floor", "3rd Floor",
    "4th Floor", "5th Floor", "6th Floor", "7th Floor",
]

# ── Project registry: add new projects here ──────────────────────────────────
PROJECT_REGISTRY = [
    {
        "slug": "kala-chowki",
        "id": 1,
        "name": "Kala Chowki Project",
        "display_name": "Kalyan Kala Chowk",
        "tagline": "Premium Commercial Complex",
        "location": "Kalyan (W), Thane, Maharashtra",
        "type": "Commercial Complex",
        "status": "ongoing",
        "progress": 10,
        "shops": 217,
        "parking": "180 Scooters / 217 Cars",
        "launch_date": "Q2 2024",
        "possession_date": "Q4 2026",
        "rera_id": "P51700012345",
        "total_area_sqft": 339791.47,
        "floors": 7,
    },
]

DEFAULT_IMAGES = {
    "hero": "/images/hero.jpg",
    "cover": "/images/cover.jpg",
    "thumbnail": "/images/thumbnail.jpg",
    "construction": "/images/construction.jpg",
    "gallery": [
        "/images/gallery-1.jpg",
        "/images/gallery-2.jpg",
        "/images/gallery-3.jpg",
        "/images/gallery-4.jpg",
    ],
}


def build_project(meta: dict) -> dict:
    slug = meta["slug"]
    assets = load_project_assets(slug)
    images = {**DEFAULT_IMAGES}
    if assets["gallery_urls"]:
        images["gallery"] = assets["gallery_urls"]

    return {
        **meta,
        "floor_list": FLOORS if meta["slug"] == "kala-chowki" else FLOORS[: meta["floors"] + 1],
        "images": images,
        "categories": PROJECT_CATEGORIES,
        "construction_phases": CONSTRUCTION_PHASES,
        "documents": assets["documents"],
        "maps": assets["maps"],
        "floor_plans": assets["floor_plans"],
        "data_folder": assets["data_path"],
    }


def all_projects() -> list[dict]:
    return [build_project(meta) for meta in PROJECT_REGISTRY]


def _safe_file(base: Path, filename: str) -> Path:
    path = (base / filename).resolve()
    if not str(path).startswith(str(base.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return path


@app.get("/")
def home():
    return {
        "message": "Malkar Enterprises API Running",
        "projects": len(PROJECT_REGISTRY),
        "upload_hint": str(DATA_ROOT),
    }


@app.get("/projects")
def get_projects():
    return all_projects()


@app.get("/projects/{project_id}")
def get_project(project_id: int):
    for p in all_projects():
        if p["id"] == project_id:
            return p
    raise HTTPException(status_code=404, detail="Project not found")


@app.get("/projects/{slug}/documents/{filename}")
def get_project_document(slug: str, filename: str):
    base = DATA_ROOT / slug / "documents"
    path = _safe_file(base, filename)
    return FileResponse(
        path=path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{path.name}"'},
    )


@app.get("/projects/{slug}/maps/{filename}")
def get_project_map(slug: str, filename: str):
    base = DATA_ROOT / slug / "maps"
    path = _safe_file(base, filename)
    media = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return FileResponse(path=path, media_type=media)


@app.get("/projects/{slug}/gallery/{filename}")
def get_project_gallery_image(slug: str, filename: str):
    base = DATA_ROOT / slug / "gallery"
    path = _safe_file(base, filename)
    media = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return FileResponse(path=path, media_type=media)


# Legacy routes (kept for older links)
@app.get("/documents/{doc_id}")
def get_document_legacy(doc_id: str):
    for p in all_projects():
        for doc in p["documents"]:
            if doc["id"] == doc_id:
                return get_project_document(p["slug"], doc["filename"])
    raise HTTPException(status_code=404, detail="Document not found")


@app.get("/maps/{map_id}")
def get_map_legacy(map_id: str):
    for p in all_projects():
        for m in p["maps"]:
            if m["id"] == map_id:
                return get_project_map(p["slug"], m["filename"])
    raise HTTPException(status_code=404, detail="Map not found")


@app.post("/enquiries")
def submit_enquiry(payload: dict = Body(...)):
    try:
        record = save_enquiry(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Could not save your enquiry. Please try again.") from exc

    return {
        "success": True,
        "id": record["id"],
        "message": "Thank you. Our team will contact you shortly.",
    }


@app.get("/enquiries/storage")
def enquiries_storage_path():
    """Where lead files are saved (for your reference)."""
    return {
        "json": str((Path(enquiries_data_dir()) / "enquiries.json").resolve()),
        "csv": str((Path(enquiries_data_dir()) / "enquiries.csv").resolve()),
    }
