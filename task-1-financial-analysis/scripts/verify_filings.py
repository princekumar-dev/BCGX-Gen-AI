"""
Cross-verify extracted XBRL figures against the actual rendered 10-K financial
statements on SEC EDGAR (the R*.htm files accompanying each filing).

Accessions used:
  Apple  FY2025 10-K : 0000320193-25-000079  (income stmt 2023-25, BS 2024-25, CF 2023-25)
  Apple  FY2024 10-K : 0000320193-24-000123  (BS 2023 comparative)
  Tesla  FY2025 10-K : 0001628280-26-003952
  Tesla  FY2025 10-K/A: 0001104659-26-053166 (user-provided link - check contents)
  Tesla  FY2024 10-K : 0001628280-25-003063  (BS 2023 comparative)
  MSFT   FY2026 10-K : 0001193125-26-323660  (user-provided link; FY24-25 comparatives)
  MSFT   FY2025 10-K : 0000950170-25-100235
  MSFT   FY2024 10-K : 0000950170-24-087843  (BS 2023 comparative)
"""

import os
import re
import time
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = "Financial Research Project princ@example.com"
RAW = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "raw_sec_data", "filings",
)
os.makedirs(RAW, exist_ok=True)


def get(url, binary=False):
    name = re.sub(r"[^A-Za-z0-9._-]", "_", url.split("/")[-1]) or "index.htm"
    key = url.split("/Archives/edgar/data/")[1].replace("/", "_")
    cache = os.path.join(RAW, key)
    if os.path.exists(cache):
        data = open(cache, "rb").read()
    else:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        with open(cache, "wb") as f:
            f.write(data)
        time.sleep(0.15)
    return data if binary else data.decode("utf-8", errors="replace")


def strip_rows(html):
    """Convert an HTML table to pipe-delimited text rows."""
    html = re.sub(r"</tr\s*>", "\x00", html, flags=re.I)
    html = re.sub(r"</t[dh]\s*>", " | ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", "", html)
    html = html.replace("\n", " ").replace("\t", " ")
    for a, b in (("&#160;", " "), ("&nbsp;", " "), ("&amp;", "&"),
                 ("&#8217;", "'"), ("&#8211;", "-"), ("&#8212;", "-")):
        html = html.replace(a, b)
    rows = []
    for ln in html.split("\x00"):
        ln = re.sub(r"\s+", " ", ln).strip(" |")
        if ln:
            rows.append(ln)
    return rows


KEYWORDS = [
    "total revenue", "total net sales", "net sales", "revenues",
    "net income", "total assets", "total liabilities",
    "operating activities", "cash provided by operating",
]


def show_statement(cik, accn, label, stmt_keywords):
    base = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accn.replace('-', '')}"
    print(f"\n{'='*100}\n{label}\n{base}/\n{'='*100}")
    fs = get(base + "/FilingSummary.xml")
    root = ET.fromstring(fs)
    reports = []
    for rep in root.iter("Report"):
        sn = rep.findtext("ShortName") or ""
        fn = rep.findtext("HtmlFileName") or rep.findtext("XmlFileName") or ""
        reports.append((sn, fn))
    shown = 0
    for sn, fn in reports:
        low = sn.lower()
        if (any(k in low for k in stmt_keywords)
                and "parenthetical" not in low
                and "detail" not in low
                and "schedule" not in low):
            print(f"\n--- [{sn}] ({fn}) ---")
            try:
                rows = strip_rows(get(f"{base}/{fn}"))
            except Exception as e:
                print(f"   fetch error: {e}")
                continue
            for ln in rows:
                low_ln = ln.lower()
                if (any(k in low_ln for k in KEYWORDS)
                        and any(c.isdigit() for c in ln)
                        and not low_ln.startswith("- definition")
                        and "defref" not in low_ln):
                    print("   ", ln[:220])
            shown += 1
            if shown >= 4:
                break


if __name__ == "__main__":
    # ---- Apple ----
    show_statement("320193", "0000320193-25-000079",
                   "APPLE FY2025 10-K (user link: aapl-20250927.htm)",
                   ["statements of operations", "income", "balance sheet",
                    "financial position", "cash flows"])
    show_statement("320193", "0000320193-24-000123",
                   "APPLE FY2024 10-K (FY2023 balance sheet comparative)",
                   ["balance sheet", "financial position"])
    # ---- Tesla ----
    show_statement("1318605", "0001628280-26-003952",
                   "TESLA FY2025 10-K (financial statements)",
                   ["statements of operations", "income", "balance sheet",
                    "financial position", "cash flows"])
    show_statement("1318605", "0001628280-25-003063",
                   "TESLA FY2024 10-K (FY2023 balance sheet comparative)",
                   ["balance sheet", "financial position"])
    # ---- Tesla 10-K/A (user-provided link: tm2611837d1_10ka.htm) ----
    try:
        doc = get("https://www.sec.gov/Archives/edgar/data/1318605/"
                  "000110465926053166/tm2611837d1_10ka.htm")
        txt = re.sub(r"<[^>]+>", " ", doc)
        txt = re.sub(r"\s+", " ", txt)
        print(f"\n{'='*100}\nTESLA 10-K/A (user link tm2611837d1_10ka.htm) - first 600 chars:\n{'='*100}")
        print(txt[:600])
    except Exception as e:
        print("tesla 10-K/A fetch error:", e)
    # ---- Microsoft ----
    show_statement("789019", "0001193125-26-323660",
                   "MICROSOFT FY2026 10-K (user link: msft-20260630.htm; FY24-25 comparatives)",
                   ["income", "balance sheet", "financial position", "cash flows"])
    show_statement("789019", "0000950170-25-100235",
                   "MICROSOFT FY2025 10-K (FY2025 & FY2023 statements)",
                   ["income", "balance sheet", "financial position", "cash flows"])
    show_statement("789019", "0000950170-24-087843",
                   "MICROSOFT FY2024 10-K (FY2023 balance sheet comparative)",
                   ["balance sheet", "financial position"])
