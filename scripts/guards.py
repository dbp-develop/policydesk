"""Shared checks for fetch and build scripts (stdlib only).

Redirects must stay on the host that was requested. Response bodies and zip
members are size-capped. Official profile URLs must use the parliament host
already present on current member records. A bad fetched_at is an error.
"""

from __future__ import annotations

import urllib.parse
import zipfile

# Stops a redirected multi-gigabyte body. Boundary zips in use are far smaller
# (the AEC national ESRI zip is about 22 MB).
MAX_HTTP = 32 * 1024 * 1024
MAX_BOUNDARY = 128 * 1024 * 1024
MAX_ZIP_MEMBER = 256 * 1024 * 1024

# Hosts seen on official_url in the committed member files.
HOSTS = {
    "vic": {"www.parliament.vic.gov.au"},
    "federal": {"handbook.aph.gov.au"},
    "nsw": {"www.parliament.nsw.gov.au"},
    "qld": {"www.parliament.qld.gov.au"},
    "wa": {"www.parliament.wa.gov.au"},
    "sa": {"www.parliament.sa.gov.au"},
    "tas": {"www.parliament.tas.gov.au"},
    "act": {"www.parliament.act.gov.au"},
    "nt": {"parliament.nt.gov.au"},
}

# Statewide upper houses and the Senate use these region names for every
# member of that state. Another member of the same region does not fill one
# vacancy. Tasmanian Legislative Council divisions are not in this set.
JURISDICTION_REGIONS = {
    "victoria",
    "new south wales",
    "queensland",
    "western australia",
    "south australia",
    "tasmania",
    "australian capital territory",
    "northern territory",
}


def read_limited(stream, limit: int) -> bytes:
    """Read until EOF, refusing a body larger than limit."""
    buf = bytearray()
    while True:
        chunk = stream.read(min(65536, limit + 1))
        if not chunk:
            break
        if len(buf) + len(chunk) > limit:
            raise RuntimeError(f"response exceeds {limit} bytes")
        buf += chunk
    return bytes(buf)


def read_checked(
    resp,
    requested_url: str,
    *,
    limit: int = MAX_HTTP,
    extra_hosts: tuple[str, ...] = (),
) -> bytes:
    """Read a urlopen response only if the final host is the one requested.

    extra_hosts is for a known second host of that one URL (Commons FilePath
    redirects to upload.wikimedia.org). Parliament and news fetches pass none.
    """
    final = resp.geturl()
    got = urllib.parse.urlsplit(final).netloc.lower()
    want = urllib.parse.urlsplit(requested_url).netloc.lower()
    allowed = {want, *(h.lower() for h in extra_hosts)}
    if not want or got not in allowed:
        raise RuntimeError(
            f"refusing response from {got!r} for request to {want!r} ({final})"
        )
    return read_limited(resp, limit)


def read_zip_member(zf: zipfile.ZipFile, name: str, limit: int = MAX_ZIP_MEMBER) -> bytes:
    """Read one zip member, refusing a claimed or actual expansion over limit."""
    info = zf.getinfo(name)
    if info.file_size > limit:
        raise RuntimeError(f"zip member {name} claims {info.file_size} bytes")
    with zf.open(name, "r") as handle:
        return read_limited(handle, limit)


def iso_date(value: str | None) -> str:
    """Return YYYY-MM-DD from an ISO timestamp. Never substitute today."""
    from datetime import datetime

    if not value or not str(value).strip():
        raise ValueError("missing fetched_at")
    text = str(value).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).date().isoformat()
    except ValueError as exc:
        raise ValueError(f"unparseable fetched_at {value!r}") from exc


def profile_host_ok(url: str | None, hosts: set[str]) -> bool:
    if not url or not str(url).startswith("https://"):
        return False
    host = urllib.parse.urlsplit(url).netloc.lower()
    return host in {h.lower() for h in hosts}


def assert_profile_urls(members: list[dict], hosts: set[str], field: str = "url") -> None:
    """Raise if any profile URL is missing or not on the parliament host."""
    bad: list[str] = []
    for member in members:
        url = member.get(field)
        if not profile_host_ok(url, hosts):
            bad.append(f"{member.get('name')}: {url}")
    if bad:
        shown = "; ".join(bad[:8])
        raise RuntimeError(
            "official profile URL is not on the parliament host: " + shown
        )


def _house(label: str | None) -> str | None:
    if label in {"Assembly", "House", "lower"}:
        return "lower"
    if label in {"Council", "Senate", "upper"}:
        return "upper"
    return None


def member_build_error(
    parliament: str, members: list[dict], vacancies: list[dict]
) -> str | None:
    """None if members.json may be written. Otherwise a line for the Action log."""
    filled = filled_vacancy_seat(members, vacancies)
    if filled:
        return f"VACANCY FILLED: {filled}"
    try:
        assert_profile_urls(members, HOSTS[parliament], "official_url")
    except RuntimeError as exc:
        return f"ERROR: {exc}"
    return None


def _seat_counts(members: list[dict], chamber: str, field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for member in members:
        if member.get("chamber") != chamber:
            continue
        seat = member.get(field)
        if seat:
            counts[seat] = counts.get(seat, 0) + 1
    return counts


def _seat_is_full(counts: dict[str, int], seat: str | None) -> bool:
    """True when this seat already has its full member count.

    A single-member seat is full when one member holds it. A multi-member
    seat (Tasmanian Assembly divisions, ACT electorates, Victorian Council
    regions) is full only when the sitting count equals the most members
    any seat in that chamber currently has. That maximum is the full
    complement while at least one seat is full, so one resignation in a
    seven-member division does not look filled.
    """
    if not seat or not counts:
        return False
    sitting = counts.get(seat, 0)
    size = max(counts.values())
    return sitting > 0 and sitting == size


def filled_vacancy_seat(members: list[dict], vacancies: list[dict]) -> str | None:
    """Seat name when vacancies.json still lists a seat that is already full.

    A human edits the vacancy file in the same change as the new member.
    Until that edit exists, the build fails with this seat name and does not
    write members.json. The Action opens an issue and leaves main unchanged.

    A statewide upper-house region (a Senate state, or the NSW, WA, or SA
    Council) is shared. Other members of that region do not fill one vacancy.
    """
    lower_counts = _seat_counts(members, "lower", "electorate")
    upper_counts = _seat_counts(members, "upper", "region")

    for vacancy in vacancies:
        house = _house(vacancy.get("chamber"))
        if house == "lower":
            seat = vacancy.get("electorate")
            if _seat_is_full(lower_counts, seat):
                return seat
        elif house == "upper":
            seat = vacancy.get("region") or vacancy.get("electorate")
            if not seat or str(seat).casefold() in JURISDICTION_REGIONS:
                continue
            if _seat_is_full(upper_counts, seat):
                return seat
    return None


def deed_needle(licence_name: str) -> str | None:
    """Path fragment that must appear in the Creative Commons deed URL."""
    import re

    name = (licence_name or "").strip().lower()
    if name.startswith("cc0"):
        return "publicdomain/zero/1.0"
    match = re.match(r"cc by(-sa)? (\d+\.\d+)", name)
    if not match:
        return None
    kind = "by-sa" if match.group(1) else "by"
    return f"licenses/{kind}/{match.group(2)}"


def url_for_licence(name: str, urls: list[str]) -> str | None:
    """Pick the deed URL that belongs to this licence name, not by list index."""
    needle = deed_needle(name)
    lowered = (name or "").strip().lower()
    if lowered.startswith("public domain"):
        found = [u for u in urls if "publicdomain" in u.lower()]
        return found[0] if found else None
    if not needle:
        return None
    found = [u for u in urls if needle in u.lower()]
    if found:
        return found[0]
    if lowered.startswith("cc0"):
        return "https://creativecommons.org/publicdomain/zero/1.0/"
    return None


def md_cell(value: str | None) -> str:
    """Escape text placed in a GitHub-flavoured markdown table cell."""
    text = (value or "").replace("\r", " ").replace("\n", " ")
    text = text.replace("\\", "\\\\").replace("|", "\\|")
    text = text.replace("[", "\\[").replace("]", "\\]")
    # Break a markdown link even if a renderer ignores the backslashes.
    return text.replace("](", "] (")
