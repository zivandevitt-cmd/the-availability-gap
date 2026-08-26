#!/usr/bin/env python3
"""Build the recruiter-first README, portable landing page and hosting notes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
payload = json.loads((ROOT / "analysis" / "executive_summary.json").read_text())
S, F = payload["summary"], payload["findings"]


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def money(value: float) -> str:
    return f"R{value / 1_000_000:,.2f}m" if abs(value) >= 1_000_000 else f"R{value / 1_000:,.1f}k"


def build(live_url: str | None) -> None:
    dashboard_href = f"{live_url.rstrip('/')}/dashboard/index.html" if live_url else "dashboard/Morrowfield_Availability_Margin_Dashboard.html"
    dashboard_note = "Verified hosted interactive dashboard" if live_url else "Self-contained dashboard; enable GitHub Pages for browser hosting"
    screenshot = next(
        (
            candidate
            for candidate in ("images/executive-overview.jpg", "images/executive-overview.png")
            if (ROOT / candidate).exists()
        ),
        "images/hero-linkedin.png",
    )

    readme = f"""
# The Availability Gap

**A retailer reported {pct(S['availability_pct'])} availability. Its tracked stock data still revealed {money(S['estimated_lost_sales'])} in estimated missed sales.**

### Business problem

Morrowfield Food Co., a fictional South African grocer, needed to understand why a healthy national availability figure was hiding concentrated supplier, store and product exposure while its highest-sales region was experiencing margin pressure.

### Key result

**One supplier accounted for {pct(F['top_supplier_lost_sales_share'])} of estimated missed sales. Ten products explained {pct(F['top_ten_product_lost_share'])} of the opportunity.**

### Tools

Excel · SQL · Power Query · Power BI-ready DAX · Python · SQLite · Interactive HTML

### Explore

- [Interactive dashboard]({dashboard_href}) — {dashboard_note}.
- [Download the Excel workbook](excel/Morrowfield_Availability_Margin_Analyst_Workbook.xlsx).
- [Inspect the ten management SQL queries](sql/02_management_questions.sql).
- [Explore the clean dataset and SQLite database](data/clean/).
- [Read the management assignment](documentation/02-management-brief.md).
- [View the analytical data model](images/data-model.png).

![The Availability Gap: executive overview]({screenshot})

## Business problem

The business question was not “build a sales dashboard.” It was whether store-level supplier service, tracked inventory, promotional activity and gross margin could explain a commercial gap that the chain-wide availability percentage did not expose.

Management needed to decide which supplier to escalate, which stores and products to protect, whether promotional guardrails were required and how much modelled exposure might be recoverable.

## Management questions

1. How do sales, gross profit and gross margin compare with the approved store-level plan?
2. Which regions, stores, products and suppliers create the largest tracked availability gap?
3. Do delayed and incomplete deliveries coincide with the same location and product exceptions?
4. How concentrated is estimated lost sales exposure?
5. Is strong revenue disguising a separate promotional margin weakness?
6. Which actions are supported by evidence, and which remain hypotheses?

## Dataset

| Clean source | Grain | Rows |
|---|---|---:|
| Weekly sales and returns | Store, product, week and record type | {S['sales_records']:,} |
| Tracked inventory snapshots | Store, tracked product and week | {S['inventory_records']:,} |
| Supplier purchase orders | Individual purchase order | {S['purchase_orders']:,} |
| Store targets | Store and week | {S['stores'] * S['weeks']:,} |
| Store dimension | Approved branch | {S['stores']} |
| Product dimension | Approved assortment SKU | {S['products']} |
| Supplier dimension | Approved primary supplier | {S['suppliers']} |

The extract covers four South African regions and 26 completed trading weeks. The tracked inventory range does not include every product; the limitation is documented in each relevant measure.

## Data quality and cleaning

The raw sources contain repeated extract rows, trailing spaces in join keys, mixed date formats, percentage values supplied as text, missing transaction costs, inconsistent category and region labels, duplicate product master records and unmapped identities.

- **{S['quality_issues']}** distinct source-quality issues were logged.
- **{S['quarantined_sales_records']}** unmapped sales records were quarantined instead of guessed.
- **{S['return_records']:,}** legitimate return records were retained despite negative values.
- Every approved primary key, join, financial arithmetic check and management control total was reconciled.

See the [full data quality log](qa/data_quality_log.csv) and [cross-source reconciliation controls](qa/reconciliation_checks.json).

## Data model

Sales, inventory, supplier orders and store targets remain separate fact tables. Calendar, store, product and supplier dimensions provide consistent filtering. Store-level targets are never repeated at product or supplier grain.

![Conformed dimensions and separate fact tables](images/data-model.png)

[Read the model and relationship documentation](documentation/04-data-model.md).

## KPI framework

| Measure | Result | Rule |
|---|---:|---|
| Net sales | {money(S['net_sales'])} | Signed gross sales less discounts, including returns. |
| Sales target attainment | {pct(S['target_attainment_pct'])} | Net sales divided by approved store-week targets. |
| Gross profit | {money(S['gross_profit'])} | Net sales less recorded product cost. |
| Gross margin | {pct(S['gross_margin_pct'])} | Gross profit divided by net sales. |
| Demand-weighted availability | {pct(S['availability_pct'])} | Fulfilled tracked demand divided by expected tracked demand. |
| Estimated missed sales | {money(S['estimated_lost_sales'])} | Category-adjusted missed demand multiplied by realised price. |
| Estimated missed gross profit | {money(S['estimated_lost_gross_profit'])} | Category-adjusted missed demand multiplied by unit gross margin. |
| Supplier fill rate | {pct(S['supplier_fill_rate'])} | Received units divided by ordered units. |

[Download the complete KPI dictionary](documentation/kpi-dictionary.csv).

## SQL

The SQL script answers ten actual management questions using CTEs, joins, `CASE`, ranking, `LAG`, `LEAD`, rolling averages, cumulative contribution and source-integrity checks. Each cross-fact analysis aggregates to the correct common grain before joining.

- [Analytical schema](sql/01_schema.sql)
- [Ten tested management questions](sql/02_management_questions.sql)

## Excel and Power Query

The fourteen-sheet workbook includes an executive view, complete weekly controls, regional scorecard, store priorities, product Pareto, supplier service, promotion review, management actions, data-quality log, reconciliation sheet, KPI dictionary, reviewed sales/inventory samples and every supplier order.

Workbook samples are transparently labelled; complete source extracts remain available in `data/clean/`.

- [Excel analyst workbook](excel/Morrowfield_Availability_Margin_Analyst_Workbook.xlsx)
- [Power Query transformation reference](powerbi/01_power_query_transformations.pq)
- [Power BI-ready DAX measure library](powerbi/02_dax_measure_library.dax)

## Analysis and root cause

The headline was misleading in a specific way:

- Overall tracked availability was **{pct(S['availability_pct'])}**, above a 94% threshold.
- **{F['top_supplier_name']}** accounted for **{pct(F['top_supplier_lost_sales_share'])}** of estimated missed sales.
- Its observed fill rate was **{pct(F['top_supplier_fill_rate'])}**; on-time delivery was **{pct(F['top_supplier_on_time_rate'])}**.
- The ten highest-loss products explained **{pct(F['top_ten_product_lost_share'])}** of the total opportunity.
- Gauteng generated **{pct(F['discount_region_sales_share'])}** of recorded sales, while its winter promotion realised only **{pct(F['winter_promotion_margin'])}** gross margin.

Supplier service and stock gaps are associated in the selected locations and weeks. The available source does not prove which operating issue caused the failures.

[Read the complete findings and rejected hypotheses](documentation/03-analysis-and-findings.md).

## Financial impact

The tracked-range opportunity is an estimate, not recorded revenue. Chilled items use a 74% demand-capture factor; other monitored categories use 68%. An additional 58% illustrative recovery scenario produces approximately **{money(F['illustrative_recoverable_sales'])}** in recoverable sales and **{money(F['illustrative_recoverable_gross_profit'])}** in recoverable gross profit before intervention costs.

[Review the financial assumptions and boundaries](documentation/05-financial-impact-methodology.md).

## Recommendations

1. Escalate the lead cold-chain supplier and protect the highest-loss chilled products.
2. Introduce a twice-weekly exception review for the most exposed coastal stores.
3. Apply realised-margin guardrails to deep Gauteng household and personal-care promotions.
4. Review chilled reorder buffers without ignoring spoilage and cold-room constraints.
5. Join supplier service, tracked availability and ownership in a weekly management review.

## Dashboard

The self-contained report includes seven working analytical views: executive overview, commercial performance, product/store performance, supplier operations, root cause, financial impact and action centre. Global period, region, category, supplier and store filters update the relevant calculations.

## Limitations

- The company and commercial records are fictional.
- Inventory only covers the designated tracked range.
- Demand, capture and recoverable opportunity are estimated.
- Customer substitution, stock expiry, store-transfer costs and supplier incident reports are unavailable.
- Promotional comparisons are descriptive; they do not establish causal incremental return.
- The DAX library is Power BI-ready but is not presented as an already published `.pbix` file.

## Repository structure

```text
morrowfield-retail-availability-intelligence/
├── README.md
├── LICENSE
├── index.html
├── analysis/
├── dashboard/
├── data/
│   ├── raw/
│   └── clean/
├── documentation/
├── excel/
├── images/
├── portfolio/
├── powerbi/
├── qa/
├── scripts/
└── sql/
```

## How to explore the project

1. Start with the [interactive dashboard]({dashboard_href}).
2. Open the [Excel workbook](excel/Morrowfield_Availability_Margin_Analyst_Workbook.xlsx) and review the Reconciliation sheet.
3. Run the [SQL queries](sql/02_management_questions.sql) against `data/clean/morrowfield_analytics.sqlite`.
4. Inspect the [raw versus clean datasets](data/) and the [documented cleaning decisions](qa/data_quality_log.csv).
5. Read the [management assignment](documentation/02-management-brief.md), [findings](documentation/03-analysis-and-findings.md) and [financial methodology](documentation/05-financial-impact-methodology.md).

## Quality assurance

The report cleared a **99.5 / 100** release gate after four independent metric-reconciliation scopes, 36 browser interaction checks, 17 legend-to-chart colour checks and responsive browser tests at 1440, 900, 600 and 390 pixels.

- [Release decision and weighted QA checklist](qa/release-checklist.md)
- [Real-browser interaction and metric evidence](qa/browser_validation.json)
- [Workbook reconciliation and formula checks](qa/workbook_validation.json)
- [Executed SQL query and integrity checks](qa/sql_validation.json)

## Skills demonstrated

Business framing; source profiling; data cleaning; conformed dimensional modelling; Excel formulas and charts; SQL CTEs and window functions; Power Query; DAX; KPI design; weighted calculations; Pareto and driver analysis; supplier diagnostics; financial opportunity sizing; report UX; management communication; and quality assurance.

## Portfolio disclaimer

This is an independent portfolio project by Zivan Devitt. Morrowfield Food Co., its suppliers, products and commercial dataset are fictional and were created to simulate a realistic retail analytics assignment.
"""
    (ROOT / "README.md").write_text(readme.strip() + "\n", encoding="utf-8")

    landing = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Availability Gap | Zivan Devitt</title><meta name="description" content="Independent retail analytics portfolio by Zivan Devitt"><style>*{{box-sizing:border-box}}body{{margin:0;background:#11161a;color:#edece8;font:15px/1.65 Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}main{{max-width:1120px;padding:48px 30px 80px;margin:auto}}.brand{{letter-spacing:.16em;font-size:15px}}.eyebrow{{margin-top:84px;color:#d0ac76;text-transform:uppercase;letter-spacing:.15em;font-size:10px}}h1{{font-size:clamp(38px,7vw,68px);line-height:1.06;letter-spacing:-.06em}}h1 span{{color:#d0ac76}}p{{max-width:760px;color:#a3acae}}.actions{{display:flex;gap:20px;flex-wrap:wrap;margin-top:26px}}a{{color:#d0ac76;text-decoration:none}}a.primary{{padding:12px 17px;background:#d0ac76;color:#171b1d}}.metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:67px;padding-top:25px;border-top:1px solid #30383c}}.metrics strong{{display:block;font-size:30px}}.metrics small{{color:#a3acae}}img{{display:block;max-width:100%;margin-top:56px;border:1px solid #30383c}}.files{{margin-top:52px}}.files li{{margin:8px 0;color:#a3acae}}footer{{margin-top:65px;color:#788286;font-size:11px}}@media(max-width:600px){{main{{padding:30px 18px}}.eyebrow{{margin-top:58px}}.metrics{{grid-template-columns:1fr 1fr}}}}</style></head><body><main><div class="brand">MORROWFIELD / CASEFILE 01</div><div class="eyebrow">Independent data analytics portfolio · Zivan Devitt</div><h1>The number looked healthy.<br><span>The shelves told a different story.</span></h1><p>A fictional South African grocery retailer reported {pct(S['availability_pct'])} availability. Its linked supplier and stock data revealed {money(S['estimated_lost_sales'])} in estimated missed sales and a separate promotion-margin weakness.</p><div class="actions"><a class="primary" href="dashboard/Morrowfield_Availability_Margin_Dashboard.html">Open the interactive dashboard ↗</a><a href="excel/Morrowfield_Availability_Margin_Analyst_Workbook.xlsx">Download the Excel workbook ↗</a></div><section class="metrics"><div><strong>{S['sales_records']:,}</strong><small>clean sales records</small></div><div><strong>{pct(F['top_supplier_lost_sales_share'])}</strong><small>of estimated missed sales linked to one supplier</small></div><div><strong>{pct(F['top_ten_product_lost_share'])}</strong><small>of exposure concentrated in ten products</small></div></section><img src="{screenshot}" alt="The Availability Gap analytics project"><section class="files"><h2>Inspect the actual work</h2><ul><li><a href="sql/02_management_questions.sql">Ten executable SQL management analyses</a></li><li><a href="documentation/02-management-brief.md">Business assignment and reporting scope</a></li><li><a href="documentation/03-analysis-and-findings.md">Evidence, findings and rejected hypotheses</a></li><li><a href="powerbi/02_dax_measure_library.dax">Power BI-ready DAX measure library</a></li><li><a href="images/data-model.png">Conformed analytical data model</a></li></ul></section><footer>Independent portfolio project. Morrowfield Food Co. and its commercial dataset are fictional.</footer></main></body></html>"""
    (ROOT / "index.html").write_text(landing, encoding="utf-8")

    hosting = """
# Publication and free-hosting notes

## Preferred account-owned publication

Create one dedicated public repository named `morrowfield-retail-availability-intelligence` in the authenticated `zivandevitt-cmd` GitHub account. Upload the complete prepared project, retaining the existing folder structure, `README.md`, `index.html`, `.gitignore` and license.

The connected GitHub integration needs permission to create a repository and write its contents. A prepared local project or hosted portfolio is not evidence that a GitHub repository already exists.

## Free GitHub Pages option

GitHub documents that GitHub Pages is available for public repositories on GitHub Free. Its branch-publishing guide allows the publishing source to be the repository root or a `/docs` directory.

1. Create and populate the public project repository.
2. Open repository Settings → Pages.
3. Under Build and deployment, choose Deploy from a branch.
4. Select the `main` branch and the `/(root)` folder.
5. Save the selection and wait for GitHub to show the actual published URL.
6. Verify `index.html`, the dashboard, workbook and SQL links from that actual URL.

Official documentation: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## Cloudflare Pages alternative

Cloudflare's published Pages limits currently list 500 builds per month on its Free plan. Confirm the latest account limits, individual file-size restrictions and eligibility before deployment.

Official documentation: https://developers.cloudflare.com/pages/platform/limits/

Do not invent a GitHub repository URL, GitHub Pages URL or Cloudflare Pages URL. Record and share only links returned by the successful publishing platform.
"""
    (ROOT / "documentation" / "07-hosting-and-publication.md").write_text(hosting.strip() + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "readme": str(ROOT / "README.md"), "live_url": live_url, "screenshot": screenshot}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-url", default=None)
    args = parser.parse_args()
    build(args.live_url)
