from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = BACKEND_ROOT / "data" / "projects"
API_BASE = "http://127.0.0.1:8000"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
DOC_EXTS = {".pdf"}


def _slug_dir(slug: str) -> Path:
    return DATA_ROOT / slug


def _scan_pdfs(docs_dir: Path, slug: str) -> list[dict]:
    items = []
    if not docs_dir.is_dir():
        return items
    for path in sorted(docs_dir.iterdir()):
        if path.suffix.lower() not in DOC_EXTS or not path.is_file():
            continue
        doc_id = f"{slug}-{path.stem}".lower().replace(" ", "-")[:80]
        items.append(
            {
                "id": doc_id,
                "name": path.stem.replace("_", " "),
                "filename": path.name,
                "url": f"{API_BASE}/projects/{slug}/documents/{path.name}",
                "available": True,
            }
        )
    return items


def _scan_images(folder: Path, slug: str, route: str) -> list[dict]:
    items = []
    if not folder.is_dir():
        return items
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in IMAGE_EXTS or not path.is_file():
            continue
        item_id = f"{slug}-{path.stem}".lower().replace(" ", "-")[:80]
        items.append(
            {
                "id": item_id,
                "name": path.stem.replace("_", " ").replace("-", " ").title(),
                "filename": path.name,
                "url": f"{API_BASE}/projects/{slug}/{route}/{path.name}",
                "available": True,
            }
        )
    return items


def _floor_plans(maps: list[dict]) -> dict[str, str]:
    """Map floor label -> image URL using filename hints (e.g. 3rd-floor.png)."""
    plans: dict[str, str] = {}
    floor_aliases = {
        "basement": "Basement",
        "ground": "Ground",
        "1st": "1st Floor",
        "2nd": "2nd Floor",
        "3rd": "3rd Floor",
        "4th": "4th Floor",
        "5th": "5th Floor",
        "6th": "6th Floor",
        "7th": "7th Floor",
    }
    for m in maps:
        stem = Path(m["filename"]).stem.lower()
        for key, label in floor_aliases.items():
            if key in stem:
                plans[label] = m["url"]
                break
    return plans


def load_project_assets(slug: str) -> dict:
    base = _slug_dir(slug)
    docs_dir = base / "documents"
    maps_dir = base / "maps"
    gallery_dir = base / "gallery"

    documents = _scan_pdfs(docs_dir, slug)
    maps = _scan_images(maps_dir, slug, "maps")
    gallery_items = _scan_images(gallery_dir, slug, "gallery")

    gallery_urls = [g["url"] for g in gallery_items]
    floor_plans = _floor_plans(maps)

    return {
        "documents": documents,
        "maps": maps,
        "gallery_urls": gallery_urls,
        "floor_plans": floor_plans,
        "data_path": str(base.resolve()),
    }
