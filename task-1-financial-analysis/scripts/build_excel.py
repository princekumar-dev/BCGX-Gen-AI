"""
Build financial_data.xlsx from the verified SEC-extracted facts.

Sheet 1 'Financial Data' - one row per company-fiscal year with the 5 metrics.
Sheet 2 'Sources & Verification' - provenance for every single data point
        (us-gaap tag, form, accession number, filing URL, filing date).
Sheet 3 'Notes' - methodology and caveats (fiscal year ends, Tesla 10-K/A).
"""

import json
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # task-1-financial-analysis/
FACTS = os.path.join(ROOT, "raw_sec_data", "extracted_facts.json")

COMPANY_ORDER = ["Microsoft", "Tesla", "Apple"]
CIK = {"Microsoft": "0000789019", "Tesla": "0001318605", "Apple": "0000320193"}
FY_END = {
    "Microsoft": "June 30, 2023|June 30, 2024|June 30, 2025",
    "Tesla": "December 31, 2023|December 31, 2024|December 31, 2025",
    "Apple": "September 30, 2023|September 28, 2024|September 27, 2025",
}
METRICS = [
    "Total Revenue",
    "Net Income",
    "Total Assets",
    "Total Liabilities",
    "Cash Flow from Operating Activities",
]

with open(FACTS, encoding="utf-8") as f:
    facts = json.load(f)

# ---------------------------------------------------------------- styles
hdr_font = Font(bold=True, color="FFFFFF", size=11)
hdr_fill = PatternFill("solid", fgColor="1F4E78")
thin = Side(style="thin", color="B0B0B0")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
NUMFMT = "#,##0"

wb = Workbook()

# =========================================================== Sheet 1
ws = wb.active
ws.title = "Financial Data"
headers = [
    "Company", "Fiscal Year", "Fiscal Year End",
    "Total Revenue (USD millions)", "Net Income (USD millions)",
    "Total Assets (USD millions)", "Total Liabilities (USD millions)",
    "Cash Flow from Operating Activities (USD millions)",
]
ws.append(headers)
for c in range(1, len(headers) + 1):
    cell = ws.cell(row=1, column=c)
    cell.font, cell.fill, cell.border = hdr_font, hdr_fill, border
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

lookup = {(x["Company"], x["Fiscal Year"], x["Metric"]): x for x in facts}
for company in COMPANY_ORDER:
    for year in (2023, 2024, 2025):
        fye = FY_END[company].split("|")[year - 2023]
        row = [company, year, fye]
        for m in METRICS:
            row.append(lookup[(company, year, m)]["Value (USD millions)"])
        ws.append(row)

for r in range(2, ws.max_row + 1):
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=r, column=c)
        cell.border = border
        if c >= 4:
            cell.number_format = NUMFMT
        if r % 2 == 0:
            cell.fill = PatternFill("solid", fgColor="DDEBF7")
widths = [12, 11, 22, 18, 18, 18, 18, 22]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "A2"

# =========================================================== Sheet 2
ws2 = wb.create_sheet("Sources & Verification")
h2 = ["Company", "Fiscal Year", "Metric", "Value (USD millions)", "Statement Line (us-gaap tag)",
      "Form", "Fiscal Period End", "Accession Number", "Source Filing (SEC EDGAR)", "Filed"]
ws2.append(h2)
for c in range(1, len(h2) + 1):
    cell = ws2.cell(row=1, column=c)
    cell.font, cell.fill, cell.border = hdr_font, hdr_fill, border
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

for x in sorted(facts, key=lambda k: (COMPANY_ORDER.index(k["Company"]), k["Fiscal Year"],
                                     METRICS.index(k["Metric"]))):
    accn = x["Accession"]
    url = f"https://www.sec.gov/Archives/edgar/data/{int(CIK[x['Company']])}/{accn.replace('-', '')}/"
    ws2.append([x["Company"], x["Fiscal Year"], x["Metric"], x["Value (USD millions)"],
                f"{x['Tag']}", x["Form"], x["Period End"], accn, url, x["Filed"]])

for r in range(2, ws2.max_row + 1):
    for c in range(1, len(h2) + 1):
        cell = ws2.cell(row=r, column=c)
        cell.border = border
        if c == 4:
            cell.number_format = NUMFMT
        if c == 9:
            cell.hyperlink = cell.value
            cell.font = Font(color="0563C1", underline="single", size=10)
for i, w in enumerate([12, 11, 32, 16, 46, 8, 14, 24, 58, 12], 1):
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.freeze_panes = "A2"

# =========================================================== Sheet 3
ws3 = wb.create_sheet("Notes")
notes = [
    ["Financial Data Extraction - Methodology & Notes", ""],
    ["", ""],
    ["Source", "SEC EDGAR 10-K filings (Forms 10-K) for Microsoft, Tesla, and Apple"],
    ["Data layer", "Inline XBRL facts (us-gaap taxonomy) reported in each 10-K, retrieved via"],
    ["", "SEC's XBRL company-facts API and cross-checked line-by-line against the"],
    ["", "rendered Consolidated Statements in the filing documents themselves."],
    ["Units", "All figures in USD millions, exactly as reported (no restatements applied)."],
    ["", ""],
    ["Fiscal years", "Each company's own fiscal year: Microsoft FY ends Jun 30; Tesla FY = calendar"],
    ["", "year; Apple FY ends late September. 'Fiscal Year 2025' therefore means the year"],
    ["", "ended 2025-06-30 (MSFT), 2025-12-31 (TSLA), 2025-09-27 (AAPL)."],
    ["", ""],
    ["Net income", "Net income (loss) attributable to the parent company (us-gaap:NetIncomeLoss)."],
    ["", "For Tesla this is 'Net income attributable to common stockholders'; consolidated"],
    ["", "net income including noncontrolling interests was 14,974 / 7,153 / 3,855."],
    ["", ""],
    ["Key filings", "Apple FY2025 10-K: accession 0000320193-25-000079 (aapl-20250927.htm);"],
    ["", "Apple FY2024 10-K: 0000320193-24-000123 (FY2023 balance sheet);"],
    ["", "Tesla FY2025 10-K: 0001628280-26-003952 (filed 2026-01-29);"],
    ["", "Tesla FY2025 10-K/A: 0001104659-26-053166 - Amendment No. 1, filed solely to add"],
    ["", "Part III governance/compensation disclosures; financial statements unchanged;"],
    ["", "Tesla FY2024 10-K: 0001628280-25-003063 (FY2023 balance sheet);"],
    ["", "Microsoft FY2026 10-K: 0001193125-26-323660 (msft-20260630.htm; FY2024-25 comparatives);"],
    ["", "Microsoft FY2025 10-K: 0000950170-25-100235; Microsoft FY2024 10-K: 0000950170-24-087843."],
    ["", ""],
    ["Verification", "All 45 data points confirmed against the rendered Consolidated Statements of"],
    ["", "Operations/Income, Balance Sheets, and Cash Flows in the filings (see script"],
    ["", "verify_filings.py and the 'Sources & Verification' sheet)."],
]
for row in notes:
    ws3.append(row)
ws3["A1"].font = Font(bold=True, size=14)
for r in range(3, ws3.max_row + 1):
    ws3.cell(row=r, column=1).font = Font(bold=True)
    ws3.cell(row=r, column=2).alignment = Alignment(wrap_text=False)
ws3.column_dimensions["A"].width = 16
ws3.column_dimensions["B"].width = 105

out = os.path.join(ROOT, "financial_data.xlsx")
wb.save(out)
print("Wrote", out)

# Also emit the CSV directly for convenience (notebook will redo Excel->CSV itself)
import csv
csv_path = os.path.join(ROOT, "financial_data.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(headers)
    for company in COMPANY_ORDER:
        for year in (2023, 2024, 2025):
            fye = FY_END[company].split("|")[year - 2023]
            w.writerow([company, year, fye] +
                       [lookup[(company, year, m)]["Value (USD millions)"] for m in METRICS])
print("Wrote", csv_path)
