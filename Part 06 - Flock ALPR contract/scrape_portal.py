"""Scrape the live Flock Safety transparency portal into a flat dict.

The portal server-renders its numbers into the page HTML, but sits behind a
Cloudflare bot check that keys on the client's TLS fingerprint, so plain
requests/curl get a 403 "Just a moment" challenge. curl_cffi impersonates a
real browser's TLS fingerprint and clears it -- no browser, Node, or Chromium
needed, and it runs synchronously (safe inside a Jupyter cell).

Which fingerprints Cloudflare accepts changes without notice: impersonating
Chrome worked daily until 2026-07-25, when Cloudflare began 403ing the entire
Chrome family (and the newest Safari builds) while Firefox and Edge still
passed. So rotate across browser *families* rather than trusting any one of
them, and space the attempts out -- firing them back-to-back gets the client
throttled, which looks identical to a fingerprint rejection.

Setup once:  pip install curl_cffi
"""
import re
import html
import time
from curl_cffi import requests as creq

PORTAL_URL = "https://transparency.flocksafety.com/boulder-co-pd"

# Ordered by what most recently cleared Cloudflare, but deliberately spanning
# families: when one family is blocked the others have kept working. Versioned
# targets missing from an older curl_cffi build are skipped, not fatal.
_IMPERSONATE = ("firefox", "edge", "safari184", "chrome", "firefox133", "safari180")

# Seconds to wait after a rejection before trying the next fingerprint.
_RETRY_DELAY = 3.0

_FIELDS = {
    "retention_days":   r"The number of days data is retained\.\s*([\d,]+)\s*days",
    "cameras":          r"Number of LPR and other cameras\.\s*([\d,]+)",
    "detections_30d":   r"Number of unique plate reads over the last 30 days\.\s*([\d,]+)",
    "hotlist_hits_30d": r"Total hotlist hits over the last 30 days\.\s*([\d,]+)",
    "searches_30d":     r"Total user search sessions over the last 30 days\.\s*([\d,]+)",
}


def _fetch(url, timeout):
    """Return the response from the first impersonation that clears Cloudflare."""
    tried = []
    for i, imp in enumerate(_IMPERSONATE):
        if i:
            time.sleep(_RETRY_DELAY)
        try:
            r = creq.get(url, impersonate=imp, timeout=timeout)
        except Exception as exc:
            # Target not built into this curl_cffi, or a transport error.
            tried.append(f"{imp}: {type(exc).__name__}")
            continue
        if r.status_code == 200 and "Just a moment" not in r.text:
            # Note the winning fingerprint in the run log -- handy when a later
            # run gets blocked and you need to know what last worked.
            print(f"cleared Cloudflare as {imp}")
            return r
        tried.append(f"{imp}: HTTP {r.status_code}")

    raise RuntimeError(
        "Cloudflare not cleared by any fingerprint (" + "; ".join(tried) + "). "
        "Flock likely tightened its bot check: run `pip install -U curl_cffi` for "
        "fresher fingerprints, then add a working target to _IMPERSONATE."
    )


def scrape_flock_portal(url=PORTAL_URL, timeout=30):
    # Fetch with a real-browser TLS fingerprint to clear Cloudflare.
    r = _fetch(url, timeout)

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
