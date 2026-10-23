"""Patch the notebook's reproducibility table to the new repo layout."""
import nbformat as nbf

nb = nbf.read('financial_analysis.ipynb', as_version=4)
repl = {
    '`fetch_sec_data.py`': '`scripts/fetch_sec_data.py`',
    '`verify_filings.py`': '`scripts/verify_filings.py`',
    '`build_excel.py`': '`scripts/build_excel.py`',
    'script: `verify_filings.py`': 'script: `scripts/verify_filings.py`',
}
n = 0
for c in nb.cells:
    if c.cell_type == 'markdown' and 'Reproducibility' in c.source:
        for a, b in repl.items():
            if a in c.source:
                c.source = c.source.replace(a, b)
                n += 1
        # raw data cache note
        c.source = c.source.replace(
            '| `financial_charts.png`, `balance_sheet_chart.png`, `financial_data_enriched.csv` | Outputs |',
            '| `financial_charts.png`, `balance_sheet_chart.png`, `financial_data_enriched.csv` | Outputs |\n'
            '| `raw_sec_data/` | Cached SEC EDGAR responses (raw JSON/XBRL + filing statements) used for verification |')
nbf.write(nb, 'financial_analysis.ipynb')
print(f'Patched {n} path references')
