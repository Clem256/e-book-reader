

def compute_scale(mode: str, zoom: float, avail_w: float, avail_h: float,
                  total_w: float, max_h: float) -> float:
    if mode == "page":
        return min(avail_w / total_w, avail_h / max_h) * 0.995
    if mode == "width":
        return (avail_w - 18) / total_w
    return zoom


class ReaderState:
    def __init__(self, doc, page: int = 0, double: bool = False):
        self.doc = doc
        self.double = double
        self.page = 0
        self.page = self.normalize(page)

    @property
    def page_count(self) -> int:
        return self.doc.page_count

    def normalize(self, p: int) -> int:
        p = max(0, min(p, self.page_count - 1))
        if self.double and p > 0 and p % 2 == 0:
            p -= 1
        return p

    def spread(self) -> list:
        if self.double and self.page > 0 and self.page + 1 < self.page_count:
            return [self.page, self.page + 1]
        return [self.page]

    def pages(self) -> list:
        return [self.doc[i] for i in self.spread()]

    def go(self, p: int):
        self.page = self.normalize(p)

    def next_index(self) -> int:
        return self.spread()[-1] + 1

    def prev_index(self) -> int:
        return self.page - 1

    def has_next(self) -> bool:
        return self.spread()[-1] < self.page_count - 1

    def has_prev(self) -> bool:
        return self.page > 0

    def toc(self) -> list:
        try:
            entries = self.doc.get_toc(simple=True)
        except Exception:
            return []
        return [(lvl, (title or "—").strip(), max(pg - 1, 0)) for lvl, title, pg in entries]

    def close(self):
        self.doc.close()
