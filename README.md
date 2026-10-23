# BCG X GenAI Job Simulation — Project Repository

This repository contains my work for the **BCG X GenAI Job Simulation** (BCG's AI-powered financial analyst project, via Forage). The simulation tasks BCG-style consultants with extracting and analyzing corporate financial data and prototyping an **AI-powered financial chatbot** to answer client questions grounded in real SEC filings.

## Repository Structure

```
BCGX-Gen-AI/
├── README.md                          ← you are here (project overview)
└── task-1-financial-analysis/
    ├── README.md                      ← Task 1 submission: full write-up & findings
    ├── financial_analysis.ipynb       ← Executed Jupyter notebook (the core deliverable)
    ├── financial_analysis.html        ← Notebook exported for submission/viewing
    ├── financial_data.xlsx            ← Compiled FY2023–FY2025 data + source provenance
    ├── financial_data.csv             ← Same data in CSV form
    ├── financial_data_enriched.csv    ← Data + derived growth % and ratios
    ├── financial_charts.png           ← Revenue / net income / margin / growth charts
    ├── balance_sheet_chart.png        ← Leverage & balance-sheet structure charts
    ├── scripts/                       ← Reproducible extraction & build pipeline
    │   ├── fetch_sec_data.py          ← Pulls the 45 verified facts from SEC EDGAR
    │   ├── verify_filings.py          ← Re-checks figures against the 10-K statements
    │   ├── build_excel.py             ← Compiles the Excel/CSV with provenance
    │   └── make_notebook.py           ← Generates the analysis notebook
    └── raw_sec_data/                  ← Cached SEC EDGAR responses (audit trail)
```

## Tasks

| # | Task | Status |
|---|------|--------|
| 1 | **10-K Financial Data Analysis** — extract FY2023–FY2025 metrics for Microsoft, Tesla & Apple from SEC EDGAR 10-K filings and analyze trends with pandas to inform an AI financial chatbot | ✅ Complete — see [`task-1-financial-analysis/`](task-1-financial-analysis/) |

## Quick Start

The analysis runs entirely in a browser-based Jupyter (no local install needed):

1. Upload `financial_analysis.ipynb` **and** `financial_data.xlsx` from `task-1-financial-analysis/` to [jupyter.org/try-jupyter](https://jupyter.org/try-jupyter/) (or Google Colab).
2. Run all cells (**Kernel → Restart Kernel and Run All Cells…**). If `openpyxl` is missing, run `%pip install openpyxl` in a cell first.
3. See **`task-1-financial-analysis/README.md`** for the full methodology and findings.

## Data Sources & Integrity

All financial figures come from the companies' **Form 10-K annual reports** filed with the U.S. SEC (EDGAR), covering fiscal years 2023–2025. Every data point was cross-verified line-by-line against the rendered financial statements in the filings themselves; provenance (accession numbers, filing URLs) is recorded in the Excel workbook and `raw_sec_data/`.

## Disclaimer

This work was prepared for a job-simulation learning exercise. It uses public SEC filing data and is **not investment advice**.
