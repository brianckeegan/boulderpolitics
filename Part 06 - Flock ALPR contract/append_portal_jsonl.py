"""Scrape the Flock transparency portal and append a snapshot to a JSONL file.

Run by the daily GitHub Action (`.github/workflows/scrape-flock-portal.yml`) to
build a time series of the Boulder PD portal. Each run appends exactly one line
to `portal_snapshots.jsonl`: the full result of `scrape_flock_portal()` plus a
`scraped_at` UTC timestamp recording when we fetched it.

Run manually with:  python append_portal_jsonl.py
"""
import json
import os
import sys
from datetime import datetime, timezone

# Make the sibling scrape_portal.py importable no matter the working directory.
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from scrape_portal import scrape_flock_portal

OUT_PATH = os.path.join(HERE, "portal_snapshots.jsonl")


def main():
    portal = scrape_flock_portal()
    record = {"scraped_at": datetime.now(timezone.utc).isoformat()}
    record.update(portal)

    line = json.dumps(record, ensure_ascii=False)
    with open(OUT_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    print(line)


if __name__ == "__main__":
    main()
