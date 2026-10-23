"""
Fetch key financial data for Microsoft, Tesla, and Apple from SEC EDGAR's XBRL API.

The XBRL "company facts" data is the machine-readable layer of the 10-K filings
themselves (each fact carries the accession number of the 10-K it came from),
so these values are exactly what appears in the filings' financial statements.

Metrics (us-gaap taxonomy):
  - Total Revenue  : RevenueFromContractWithCustomerExcludingAssessedTax (fallback: Revenues)
  - Net Income     : NetIncomeLoss
  - Total Assets   : Assets
  - Total Liabilities: Liabilities
  - Cash Flow from Operating Activities: NetCashProvidedByUsedInOperatingActivities

Fiscal years covered: 2023, 2024, 2025 (each company's own fiscal year end).
"""

import json
import os
import time
import urllib.request

# SEC requires a descriptive User-Agent with contact info
USER_AGENT = "Financial Research Project princ@example.com"
BASE = "https://data.sec.gov/api/xbrl/companyfacts/CIK{:010d}.json"

COMPANIES = {
    "Microsoft": 789019,   # CIK 0000789019, FY ends June 30
    "Tesla": 1318605,      # CIK 0001318605, FY ends Dec 31
    "Apple": 320193,       # CIK 0000320193, FY ends late Sept
}

# Preferred us-gaap tags per metric (first tag with a matching fact wins)
METRIC_TAGS = {
    "Total Revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
    ],
    "Net Income": ["NetIncomeLoss"],
    "Total Assets": ["Assets"],
    "Total Liabilities": ["Liabilities"],
    "Cash Flow from Operating Activities": [
        "NetCashProvidedByUsedInOperatingActivities",
    ],
}

# Expected fiscal year-end month for each company (used to pick annual facts)
FY_END_MONTH = {"Microsoft": 6, "Tesla": 12, "Apple": 9}

RAW_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw_sec_data"
)
os.makedirs(RAW_DIR, exist_ok=True)


def fetch_companyfacts(cik: int) -> dict:
    url = BASE.format(cik)
    cache = os.path.join(RAW_DIR, f"CIK{cik:010d}.json")
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return json.load(f)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    with open(cache, "wb") as f:
        f.write(data)
    return json.loads(data)


def annual_facts(facts: dict, tag: str, fy_years=(2023, 2024, 2025)):
    """Return {fy: fact} for annual (duration ~1yr or instant, FY) facts.

    Prefers the most recently filed/restated value for each fiscal year.
    """
    try:
        units = facts["facts"]["us-gaap"][tag]["units"]
    except KeyError:
        return {}
    unit_key = "USD" if "USD" in units else list(units)[0]
    out = {}

    for f in units[unit_key]:
        form = f.get("form", "")
        if form not in ("10-K", "10-K/A"):
            continue
        fp = f.get("fp")
        if fp != "FY":
            continue
        end = f.get("end", "")
        # Keep only facts whose end date falls in the expected FY-end month
        end_year, end_month = int(end[:4]), int(end[5:7])
        if abs(end_month - FY_END_MONTH[_current_company]) > 1:
            continue
        # For duration facts (revenue, net income, OCF) require ~1-year span
        start = f.get("start")
        if start:
            span_days = (
                int(end[:4]) * 365 + int(end[5:7]) * 30 + int(end[8:10])
            ) - (int(start[:4]) * 365 + int(start[5:7]) * 30 + int(start[8:10]))
            if span_days < 340:
                continue  # skip quarterly facts
        # Map to the fiscal year the period ENDS in
        key = end_year
        if key not in fy_years:
            continue
        prev = out.get(key)
        # Prefer most recently filed fact (latest 'filed' date => restated value)
        if prev is None or f.get("filed", "") > prev.get("filed", ""):
            out[key] = f
    return out


_current_company = "Microsoft"

def main():
    results = []
    global _current_company
    for company, cik in COMPANIES.items():
        _current_company = company
        print(f"\n=== {company} (CIK {cik}) ===")
        facts = fetch_companyfacts(cik)
        for metric, tags in METRIC_TAGS.items():
            for tag in tags:
                fy = annual_facts(facts, tag)
                if fy:
                    break
            for year in (2023, 2024, 2025):
                f = fy.get(year)
                if f is None:
                    print(f"  {metric:45s} {year}: MISSING (tag={tag})")
                    continue
                results.append({
                    "Company": company,
                    "Fiscal Year": year,
                    "Metric": metric,
                    "Value (USD millions)": round(f["val"] / 1e6, 1),
                    "Period End": f["end"],
                    "Tag": tag,
                    "Form": f["form"],
                    "Accession": f.get("accn", ""),
                    "Filed": f.get("filed", ""),
                })
                print(f"  {metric:45s} {year}: {f['val']/1e6:>12,.1f}M  "
                      f"[{f['form']} accn {f.get('accn','')} end {f['end']}]")
        time.sleep(0.3)

    with open(os.path.join(RAW_DIR, "extracted_facts.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} facts to raw_sec_data/extracted_facts.json")


if __name__ == "__main__":
    main()
