"""Scrape the live Flock Safety transparency portal into a flat dict.

The portal server-renders its numbers into the page HTML, but sits behind a
Cloudflare bot check that keys on the client's TLS fingerprint, so plain
requests/curl get a 403 "Just a moment" challenge. curl_cffi impersonates a
real Chrome TLS fingerprint and clears it -- no browser, Node, or Chromium
needed, and it runs synchronously (safe inside a Jupyter cell).

Setup once:  pip install curl_cffi
"""
import re
import html
from curl_cffi import requests as creq

PORTAL_URL = "https://transparency.flocksafety.com/boulder-co-pd"

_FIELDS = {
    "retention_days":   r"The number of days data is retained\.\s*([\d,]+)\s*days",
    "cameras":          r"Number of LPR and other cameras\.\s*([\d,]+)",
    "detections_30d":   r"Number of unique plate reads over the last 30 days\.\s*([\d,]+)",
    "hotlist_hits_30d": r"Total hotlist hits over the last 30 days\.\s*([\d,]+)",
    "searches_30d":     r"Total user search sessions over the last 30 days\.\s*([\d,]+)",
}


def scrape_flock_portal(url=PORTAL_URL, timeout=30):
    # Fetch with a real-browser TLS fingerprint to clear Cloudflare.
    last = None
    for imp in ("chrome", "chrome124", "safari"):
        r = creq.get(url, impersonate=imp, timeout=timeout)
        last = r.status_code
        if r.status_code == 200 and "Just a moment" not in r.text:
            break
    else:
        raise RuntimeError(f"Cloudflare not cleared (last status {last}); try updating curl_cffi.")

    # Strip tags -> plain text, collapse whitespace (no BeautifulSoup needed).
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", r.text, flags=re.I | re.S)
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))).strip()

    upd = re.search(r"Last updated:\s*([A-Za-z0-9 ]+?\d{4})", text)
    portal = {"updated": upd.group(1).strip() if upd else None}
    for key, pat in _FIELDS.items():
        m = re.search(pat, text, re.I)
        if not m:
            raise ValueError(f"portal layout changed; pattern not found -> {pat}")
        portal[key] = int(m.group(1).replace(",", ""))

    # "Sharing Network Data With" — each access-table cell carries the agency
    # name verbatim in a data-tp-full-value attribute on the raw HTML.
    orgs = [html.unescape(o).strip()
            for o in re.findall(r'data-tp-full-value="([^"]+)"', r.text)]
    if not orgs:
        raise ValueError("portal layout changed; agency-sharing list not found")
    portal["orgs"] = orgs
    portal["org_count"] = len(orgs)
    return portal


if __name__ == "__main__":
    from pprint import pprint
    pprint(scrape_flock_portal())
