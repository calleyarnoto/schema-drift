"""Scores schema drift severity based on comparison results."""

from dataclasses import dataclass
from schema_drift.comparator import ComparisonResult, DiffType


# Weight assigned to each diff type when computing severity score
_DIFF_WEIGHTS: dict[DiffType, int] = {
    DiffType.TABLE_ADDED: 3,
    DiffType.TABLE_REMOVED: 5,
    DiffType.COLUMN_ADDED: 2,
    DiffType.COLUMN_REMOVED: 4,
    DiffType.COLUMN_TYPE_CHANGED: 3,
    DiffType.COLUMN_NULLABLE_CHANGED: 2,
    DiffType.COLUMN_DEFAULT_CHANGED: 1,
}

_SEVERITY_THRESHOLDS: list[tuple[int, str]] = [
    (0, "none"),
    (5, "low"),
    (15, "medium"),
    (30, "high"),
]


@dataclass
class DriftScore:
    total: int
    severity: str
    breakdown: dict[str, int]

    def __repr__(self) -> str:
        return f"DriftScore(total={self.total}, severity={self.severity!r})"


def _severity_label(score: int) -> str:
    """Return a human-readable severity label for a numeric score."""
    label = "critical"
    for threshold, name in _SEVERITY_THRESHOLDS:
        if score <= threshold:
            label = name
            break
    else:
        # score exceeded all thresholds
        pass
    # Walk thresholds in reverse to find the highest bracket the score falls in
    label = "critical"
    for threshold, name in reversed(_SEVERITY_THRESHOLDS):
        if score <= threshold:
            label = name
    return label


def score_result(result: ComparisonResult) -> DriftScore:
    """Compute a drift severity score from a ComparisonResult."""
    breakdown: dict[str, int] = {dt.value: 0 for dt in DiffType}
    total = 0

    for diff in result.diffs:
        weight = _DIFF_WEIGHTS.get(diff.diff_type, 1)
        breakdown[diff.diff_type.value] += weight
        total += weight

    # Remove zero entries for cleaner output
    breakdown = {k: v for k, v in breakdown.items() if v > 0}

    return DriftScore(
        total=total,
        severity=_severity_label(total),
        breakdown=breakdown,
    )
