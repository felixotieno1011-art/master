"""Server-side structured filters for list pages.

Each service list renderer calls `apply_filter(rows, qs, spec)` where:

  rows = list of dicts (as returned by core.<service>.list_*())
  qs   = the query-string dict (from urllib.parse.parse_qs)
  spec = dict mapping query param → extractor function(record) → value

Example:
  apply_filter(instances, qs, {"state": lambda i: i.get("state", "").lower()})

The function returns the filtered list. If the param is absent or "all",
the corresponding filter is skipped.
"""
import html


def apply_filter(rows, qs, spec):
    if not rows:
        return rows
    filtered = rows
    for param, extractor in spec.items():
        values = qs.get(param) or []
        if not values:
            continue
        wanted = (values[0] or "").strip().lower()
        if not wanted or wanted == "all":
            continue
        filtered = [r for r in filtered if str(extractor(r) or "").lower() == wanted]
    return filtered


def filter_chips(qs, spec, labels=None):
    """Render a small row of 'Filtered by: state=running  ✕' chips."""
    labels = labels or {}
    parts = []
    for param in spec:
        values = qs.get(param) or []
        if not values:
            continue
        val = (values[0] or "").strip()
        if not val or val.lower() == "all":
            continue
        label = labels.get(param, param)
        parts.append(
            f'<span class="aws-filter-chip">{html.escape(label)}: '
            f'<strong>{html.escape(val)}</strong></span>'
        )
    if not parts:
        return ""
    return (
        '<div class="aws-filter-chips">Filtered by: '
        + " ".join(parts)
        + '</div>'
    )


# --- Common extractors ---

def by_state(rec):
    return rec.get("state") or rec.get("State") or ""

def by_region(rec):
    return rec.get("region") or rec.get("Region") or ""

def by_status(rec):
    return rec.get("TableStatus") or rec.get("status") or ""
