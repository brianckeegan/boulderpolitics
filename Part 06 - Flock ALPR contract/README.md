# Data sources — Charting Boulder: License Plate Readers

All primary sources used in `ALPR.ipynb`, with canonical URLs. Retrieved June 2026.

## Boulder PD search audit (the analytical spine)
- **File:** `../boulder-co-pd_org-audit_2025-06-12.csv` (committed snapshot)
- **What it is:** Flock **Organization Audit** for *Boulder CO PD* — one row per license-plate
  search **performed by Boulder Police users**, Dec 1 2024 – Jun 12 2025. Fields include the
  searching user (redacted to initials), license plate, stated `reason`, `case_number`,
  `total_networks_searched`, `total_devices_searched`, and `search_time_utc`.
- **Public mirror used:** DeFlock, "Mass Surveillance in Boulder,"
  https://blog.deflock.me/assets/docs/boulder-co-pd.csv
  (writeup: https://blog.deflock.me/alprs-in-boulder/ )
- **Cross-validation:** the implied rate (~574 searches / 30 days) matches the official
  Flock transparency portal's "Searches in the last 30 days" figure (555). See below.

## Flock transparency portal — Boulder CO PD (official, validation + sharing list)
- **URL:** https://transparency.flocksafety.com/boulder-co-pd
- **Snapshot pinned in notebook:** "Last Updated Thu Nov 27 2025." Retention 30 days; 30 cameras;
  507,558 vehicle detections / 30 days; 6,836 hotlist hits / 30 days; 555 searches / 30 days;
  90 Colorado organizations granted access (full list hard-coded in the notebook with this date).
- Portal is a **moving snapshot**; values are pinned to the retrieval date and not re-fetched at runtime.
- **Daily time series:** `portal_snapshots.jsonl` is a growing log of the portal. A GitHub Action
  (`.github/workflows/scrape-flock-portal.yml`) runs `append_portal_jsonl.py` once a day, which calls
  `scrape_portal.scrape_flock_portal()` and appends one JSON line (all portal fields plus a `scraped_at`
  UTC timestamp), then commits the result. Run it locally with `pip install curl_cffi && python append_portal_jsonl.py`.

## FOIA'd Network Audit (reported, NOT reproduced in this notebook)
- **MuckRock request:** https://www.muckrock.com/foi/boulder-172/boulder-alpr-audits-187797/
- Shows **other agencies searching Boulder's cameras** (the inbound side). Per the requester and
  404 Media, the July 2025 records show Boulder was on Flock's **national network** (thousands of
  agencies, including out-of-state and federal) and that Boulder's cameras were searched with
  reasons including "immigration." The notebook documents this as reported context; it analyzes only
  the **outbound** Organization Audit it can independently load.
- 404 Media: https://www.404media.co/ice-taps-into-nationwide-ai-enabled-camera-network-data-shows/

## City of Boulder ALPR records (context)
- **Records portal (Redfearn emails, audits):**
  https://documents.bouldercolorado.gov/WebLink/Browse.aspx?id=192695&dbid=0&repo=LF8PROD2

## Procurement documents (the decision peg) — uploaded primary sources
- RFP 24-2026, ALPR Technology & Services (issued Apr 17 2026; bids due May 29 2026); Q&A addendum.
- Appendix C — Requirements spreadsheet (the ~200 functional/privacy requirements).
- Appendix D — Master IT Agreement, incl. **Attachment C, "ALPR Camera and Footage Specific Terms."**

## State legislation (the failed alternative)
- **SB26-070**, "Ban Government Access Historical Location Information Database" (the "PEEPS Act").
  https://leg.colorado.gov/bills/sb26-070
  Would have required a warrant to search ALPR data after 72 hours, restricted cross-jurisdiction
  sharing, and made the data non-public-record. Laid over / pulled on the Senate floor, early May 2026.
