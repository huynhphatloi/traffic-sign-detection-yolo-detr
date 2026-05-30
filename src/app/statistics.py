"""Running detection statistics for the app HUD / sidebar (plan section 20.2 advanced)."""
from __future__ import annotations

from collections import defaultdict

from .inference import Detection


class DetectionStats:
    """Accumulate per-class counts and average confidence across a stream."""

    def __init__(self) -> None:
        self.count_by_class: dict[str, int] = defaultdict(int)
        self._conf_sum_by_class: dict[str, float] = defaultdict(float)
        self.frames = 0
        self.total_detections = 0

    def update(self, detections: list[Detection]) -> None:
        self.frames += 1
        self.total_detections += len(detections)
        for d in detections:
            self.count_by_class[d.cls_name] += 1
            self._conf_sum_by_class[d.cls_name] += d.conf

    def avg_conf_by_class(self) -> dict[str, float]:
        return {
            cls: self._conf_sum_by_class[cls] / n
            for cls, n in self.count_by_class.items() if n
        }

    def as_table(self) -> list[dict]:
        avg = self.avg_conf_by_class()
        return [
            {"class": cls, "count": n, "avg_conf": round(avg.get(cls, 0.0), 3)}
            for cls, n in sorted(self.count_by_class.items(), key=lambda x: -x[1])
        ]

    def reset(self) -> None:
        self.__init__()
