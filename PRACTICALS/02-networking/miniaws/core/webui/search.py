"""Service search — matches the top-bar 'Search' box of the real console."""
from core.webui import aws_ref


def find(q):
    """Return (matches, exact). Match on id, name, or description (case-insensitive)."""
    if not q:
        return [], None
    needle = q.strip().lower()
    if not needle:
        return [], None

    matches = []
    exact = None
    for sid, name, desc, href in aws_ref.SERVICES:
        hay = f"{sid} {name} {desc}".lower()
        if name.lower() == needle or sid.lower() == needle:
            exact = (sid, name, desc, href)
        if needle in hay:
            matches.append((sid, name, desc, href))

    if exact and matches and matches[0] != exact:
        matches = [exact] + [m for m in matches if m != exact]

    return matches, exact
