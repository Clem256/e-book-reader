import hashlib
from pathlib import Path

import pymupdf

from ..config import CACHE_DIR


def open_document(path: str) -> pymupdf.Document:
    return pymupdf.open(path)


def page_count(path: str) -> int:
    try:
        with pymupdf.open(path) as d:
            return 0 if d.needs_pass else d.page_count
    except Exception:
        return 0


def cover_path(path: str):
    f = CACHE_DIR / (hashlib.md5(path.encode()).hexdigest() + "_400.png")
    if not f.exists():
        try:
            with pymupdf.open(path) as d:
                if d.needs_pass:
                    return None
                p = d[0]
                z = 400 / p.rect.height
                p.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False).save(str(f))
        except Exception:
            return None
    return f


def clear_cover_cache():
    for f in CACHE_DIR.glob("*.png"):
        f.unlink(missing_ok=True)


def clean_copy(src: str, dst: str):
    with pymupdf.open(src) as d:
        d.scrub(
            javascript=True,
            attached_files=True,
            embedded_files=True,
            reset_fields=True,
            reset_responses=True,
            remove_links=True,
            hidden_text=False,
        )
        cat = d.pdf_catalog()
        for key in ("OpenAction", "AA"):
            d.xref_set_key(cat, key, "null")
        d.save(dst, garbage=4, deflate=True)
