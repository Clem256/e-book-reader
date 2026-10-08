import time
from pathlib import Path

from ..config import SORT_PROGRESS, SORT_TITLE
from . import pdf_tools


def progress_fraction(info: dict) -> float:
    n = info.get("pages", 0)
    return (info.get("page", 0) + 1) / n if n else 0.0


class Library:
    def __init__(self, storage):
        self._storage = storage
        self._books = storage.data["books"]

    def info(self, path: str) -> dict:
        return self._books[path]

    def title(self, path: str) -> str:
        return self._books[path].get("title", Path(path).stem)

    def count(self) -> int:
        return sum(1 for p in self._books if Path(p).exists())

    def entries(self, sort: int = 0, text: str = ""):
        q = text.strip().lower()
        books = [(p, i) for p, i in self._books.items()
                 if Path(p).exists() and q in i.get("title", Path(p).stem).lower()]
        if sort == SORT_TITLE:
            books.sort(key=lambda kv: kv[1].get("title", Path(kv[0]).stem).lower())
        elif sort == SORT_PROGRESS:
            books.sort(key=lambda kv: progress_fraction(kv[1]), reverse=True)
        else:
            books.sort(key=lambda kv: kv[1].get("last_opened", 0), reverse=True)
        return books

    def last_opened(self):
        recent = [(i.get("last_opened", 0), p) for p, i in self._books.items()
                  if i.get("last_opened", 0) > 0 and Path(p).exists()]
        return max(recent)[1] if recent else None

    def register(self, path: str) -> str:
        path = str(Path(path).resolve())
        if path not in self._books:
            self._books[path] = {"title": Path(path).stem, "page": 0,
                                 "pages": pdf_tools.page_count(path), "last_opened": 0}
            self._storage.schedule_save()
        return path

    def remove(self, path: str):
        self._books.pop(path, None)
        self._storage.schedule_save()

    def rename(self, path: str, title: str):
        self._books[path]["title"] = title
        self._storage.schedule_save()

    def reset_progress(self, path: str):
        self.set_page(path, 0)

    def set_page(self, path: str, page: int):
        if path in self._books:
            self._books[path]["page"] = page
            self._storage.schedule_save()

    def mark_opened(self, path: str, pages: int):
        info = self._books[path]
        info["pages"] = pages
        info["last_opened"] = time.time()
        self._storage.schedule_save()
