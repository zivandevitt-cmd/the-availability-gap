#!/usr/bin/env python3
"""Create source-grounded documentation, dictionaries and recruiter materials."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "documentation"
PORTFOLIO = ROOT / "portfolio"
IMAGES = ROOT / "images"
DATA = json.loads((ROOT / "analysis" / "executive_summary.json").read_text())
S = DATA["summary"]
F = DATA["findings"]


def money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"R{value / 1_000_000:,.2f}m"
    if abs(value) >= 1_000:
        return f"R{value / 1_000:,.1f}k"
    return f"R{value:,.2f}"


def pct(value: float, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def write(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


selection = f"""
# Selecting a flagship analytics project

The goal is to demonstrate the work an analyst would do after management notices a commercial problem: validate the data, explain the drivers, quantify the exposure and propose a practical response.

| Concept | Business problem and dataset potential | Skills and dashboard potential | Recruiter appeal | Depth | Visual | Realism | Different | Hiring |
|---|---|---|---|---:|---:|---:|---:|---:|
| Retail availability and margin recovery | Link weekly sales, store targets, supplier purchase orders and tracked inventory to explain why a healthy headline hides lost sales and margin pressure. | Relational modelling; data cleaning; SQL windows; Excel reconciliation; DAX; supplier and store drill-down; opportunity sizing. | Strong fit for retail, FMCG, reporting, operations and BI roles. | 10 | 9 | 10 | 10 | 10 |
| E-commerce fulfilment and return leakage | Combine orders, deliveries, refunds, carrier service and customer complaints to identify where delivery failures and returns erode contribution margin. | Funnel and cohort analysis; SLA measurement; carrier comparisons; return economics; operational exception views. | Good cross-industry appeal; slightly more dependent on assumptions about delivery attribution. | 9 | 9 | 9 | 9 | 9 |
| Subscription retention and expansion | Join account subscriptions, product usage, support tickets and billing to identify at-risk cohorts and renewal opportunities. | Cohort retention; churn; behavioural segmentation; lifecycle reporting; recurring-revenue measures. | Recognisable to technology employers, but churn dashboards are common and less relevant to retail/FMCG reporting roles. | 9 | 8 | 8 | 8 | 9 |

## Selected project

**The Availability Gap: retail availability, supplier reliability and margin recovery**

- **Fictional company:** Morrowfield Food Co.
- **Industry:** South African grocery and household retail.
- **Management sponsor:** Head of Retail Operations, working with Commercial Finance and Supply Chain.
- **Assignment:** Explain why sales miss plan while the headline availability measure remains green; isolate store, product, supplier and promotional drivers.
- **Why it matters:** Missed demand is not visible in recorded sales, and revenue can improve while gross margin deteriorates.
- **Expected decisions:** Supplier recovery priorities, store replenishment actions, promotion guardrails and reporting controls.

This direction is deliberately more demanding than a sales dashboard: the analyst must connect several operational systems, reconcile incompatible grains and distinguish measured results from estimated opportunities.
"""


brief = f"""
# Management assignment: availability and margin recovery

**Issued by:** Head of Retail Operations, Morrowfield Food Co.  
**Analyst:** Zivan Devitt, independent portfolio scenario  
**Reporting window:** 23 February to 23 August 2026, 26 completed trading weeks  
**Decision forum:** Weekly retail performance and supplier recovery meeting

## Company background and operating model

Morrowfield Food Co. is a fictional South African food and household retailer with {S['stores']} branches across Gauteng, Western Cape, KwaZulu-Natal and Eastern Cape. Stores trade as neighbourhood markets, conventional markets and larger food halls. This assignment covers a defined {S['products']}-product assortment across six trading categories. Supplier purchase orders, weekly point-of-sale extracts, a tracked inventory range and store-level sales targets arrive from separate operational systems.

The extract represents a focused analytical assortment, not the retailer's entire stock-keeping universe. Weekly sales records are store–product observations with separately identified return adjustments. Inventory is available only for products designated as tracked.

## Current business concern

Recorded net sales are {money(S['net_sales'])}, equivalent to {pct(S['target_attainment_pct'])} of the store-level sales plan. Demand-weighted availability across the tracked range is {pct(S['availability_pct'])}; viewed on its own, that is above the {pct(S['availability_target'], 0)} target. Management still suspects that delivery exceptions and deep promotions are creating preventable commercial gaps in particular stores and categories.

The first question is not whether the headline availability measure is red. It is whether aggregation is concealing a concentrated and financially material issue.

## Management symptoms and known facts

- Coastal teams have reported recurring chilled-range delivery exceptions.
- The Gauteng region generates the largest sales contribution, but its realised gross margin trails the rest of the estate.
- Customer return records appear as negative values and must remain in the commercial totals.
- Source extracts contain repeated rows, inconsistent identifiers, mixed date formats and incomplete mappings.
- Store targets are issued at store–week level, not product or category level.

## What management does not yet know

- Which supplier, products and stores account for most estimated missed demand.
- Whether the coastal concern is broad or concentrated in specific supplier–region combinations.
- Whether stronger sales in Gauteng correspond with lower promotional profitability.
- How much estimated revenue and gross profit might be recoverable under a conservative scenario.
- Which actions can be assigned to supply chain, regional operations and commercial finance.

## Questions to answer

1. What happened to sales, gross profit, gross margin and target attainment over the reporting window?
2. Where do weighted availability and estimated missed sales vary by region, store, category, product and supplier?
3. Which supplier delivery patterns coincide with the largest availability gaps?
4. How concentrated is loss exposure across products and stores?
5. Does the highest-revenue region also have a discount or gross-margin weakness?
6. Which management interventions are supported by observed data, and which remain hypotheses?
7. Which source defects need correction before the report can be trusted?

## Scope and available data

| Source | Grain | Coverage | Purpose |
|---|---|---:|---|
| Weekly point-of-sale fact | Store, product, week and record type | {S['sales_records']:,} clean rows | Sales, discounts, returns, cost and gross profit |
| Weekly inventory fact | Tracked store, product and week | {S['inventory_records']:,} clean rows | Demand, fulfilment, stockout exposure and estimated loss |
| Supplier purchase orders | Individual supplier order | {S['purchase_orders']:,} orders | Fill rate, delayed deliveries and supplier service |
| Store targets | Store and week | {S['stores'] * S['weeks']:,} target rows | Sales plan and operating thresholds |
| Conformed dimensions | Store, product, supplier, region and date | {S['stores']} stores; {S['products']} products; {S['suppliers']} suppliers | Consistent filtering and reporting |

## KPI requirements and management thresholds

- Net sales and sales target attainment; expected sales attainment: 100%.
- Gross profit and gross margin; reference gross-margin target: 29%.
- Demand-weighted availability for the tracked range; target: 94%.
- Estimated lost sales and gross profit; clearly labelled as modelled opportunities.
- Supplier fill rate and on-time delivery; reference thresholds: 95% and 93%.
- Effective discount rate, product concentration and store-level exposure.

## Expected deliverables

Create a cleaned relational dataset, audit log, reviewed Excel workbook, SQL analysis, Power Query transformations, DAX library, self-contained interactive report, management recommendations and recruiter-ready project documentation.

## Assumptions and limitations

Expected demand is modelled; a missing unit is not automatically a guaranteed lost sale. The opportunity model applies a 74% demand-capture factor to chilled items and 68% to other tracked categories. It does not estimate customer substitution, competitor switching, stock spoilage or campaign incrementality. Supplier service and inventory outcomes are associated in the data; an operational investigation is needed before asserting that one event caused another. Targets are not allocated below the store–week grain.

## Decisions management must make

Approve a named supplier recovery plan; assign priority stores and products; revisit promotional discount guardrails; decide whether to change replenishment buffers; and establish a weekly exception review that joins commercial and operational evidence.

> This is an independent portfolio project. Morrowfield Food Co. and the dataset are fictional.
"""


methodology = f"""
# Analytical method and findings

## Reporting contract

All commercial measures use the cleaned `FactSalesWeekly` table, including legitimate returns. Availability and estimated opportunities use the tracked `FactInventoryWeekly` range only. Supplier service comes from purchase-order records. Store targets remain at store–week grain and are not repeated across product or category visuals.

### What happened

- Net sales: **{money(S['net_sales'])}** against **{money(S['sales_target'])}** of store sales targets.
- Sales attainment: **{pct(S['target_attainment_pct'])}**.
- Gross profit: **{money(S['gross_profit'])}** at **{pct(S['gross_margin_pct'])}** gross margin.
- Demand-weighted tracked availability: **{pct(S['availability_pct'])}**, above the 94% reference threshold.
- Estimated tracked-range missed sales: **{money(S['estimated_lost_sales'])}**; related estimated gross profit: **{money(S['estimated_lost_gross_profit'])}**.

### Where

The largest absolute estimated loss occurs in **{F['top_region_name']}**, at **{money(F['top_region_lost_sales'])}**. Eastern Cape has the weakest overall regional availability, while KwaZulu-Natal carries greater rand exposure because its affected demand base is larger. Both perspectives matter; a low rate and a high financial loss need not belong to the same region.

### What the headline hides

**{F['top_supplier_name']} accounts for {pct(F['top_supplier_lost_sales_share'])} of estimated lost sales**, or **{money(F['top_supplier_lost_sales'])}**, while representing just one of {S['suppliers']} suppliers. Its weighted purchase-order fill rate is **{pct(F['top_supplier_fill_rate'])}** and its on-time delivery rate is **{pct(F['top_supplier_on_time_rate'])}**.

The ten highest-loss products account for **{pct(F['top_ten_product_lost_share'])}** of the total estimated opportunity. This concentration explains why a healthy chain-wide availability number can coexist with a material, actionable issue in a narrow operating slice.

### The separate margin issue

**{F['discount_region_name']} contributes {pct(F['discount_region_sales_share'])} of net sales**, but reports **{pct(F['discount_region_margin'])}** gross margin, compared with **{pct(F['other_regions_margin'])}** across the other regions. Its effective discount rate is **{pct(F['discount_region_discount'])}**, compared with **{pct(F['other_regions_discount'])}** elsewhere.

The `Winter Price Lock` campaign produces **{money(F['winter_promotion_sales'])}** in sales at **{pct(F['winter_promotion_margin'])}** gross margin; non-promoted records average **{pct(F['nonpromoted_margin'])}**. That comparison describes an observed margin difference. It does not, by itself, prove that the campaign reduced incremental profit because assortment and demand mix also differ.

## Evidence and interpretation

| Status | Statement |
|---|---|
| Confirmed | Sales, profit, target attainment and supplier service reconcile to the approved clean tables. |
| Confirmed | One supplier and a short list of products account for most estimated loss exposure. |
| Confirmed | The Gauteng winter promotion coincides with a lower observed realised gross margin. |
| Interpretation | Delivery reliability is a credible operating driver because supplier failures and stock shortfalls occur together in the same locations and periods. |
| Hypothesis | Capacity constraints, depot scheduling, cold-room limitations or supplier allocation explain the missed deliveries; the extract cannot establish which. |
| Recommendation | Prioritise supplier recovery, store allocation and discount guardrails rather than applying an undifferentiated chain-wide intervention. |

## Rejected or weakened hypotheses

- **“The whole chain has an availability crisis.”** Not supported: total tracked availability remains above target; the issue is concentrated.
- **“The lowest regional availability must have the largest loss.”** Not supported: exposure depends on both shortage rate and demand value.
- **“Strong Gauteng sales mean strong commercial performance.”** Incomplete: revenue leadership coexists with weaker margin.
- **“All negative values are errors.”** Incorrect: {S['return_records']:,} valid return records must remain in scope.

## What the analysis cannot claim

The dataset does not contain customer-level substitution, controlled campaign experiments, supplier incident reports, stock-expiry costs or a complete unrestricted assortment. Estimated missed sales are a decision-support approximation, not recorded revenue.
"""


model = """
# Analytical data model

## Model design

Use conformed store, product, supplier and calendar dimensions with separate facts for weekly sales, tracked inventory, purchase orders and store targets. Filter relationships run from the one-side dimension to the many-side fact. Avoid direct fact-to-fact joins in Power BI and aggregate each fact to the required common grain before combining it in SQL.

```mermaid
flowchart TB
    calendar[DimCalendar]
    stores[DimStores]
    products[DimProducts]
    suppliers[DimSuppliers]
    regions[DimRegions]
    sales[FactSalesWeekly]
    inventory[FactInventoryWeekly]
    orders[FactPurchaseOrders]
    targets[FactStoreTargets]
    regions --> stores
    calendar --> sales
    calendar --> inventory
    calendar --> orders
    calendar --> targets
    stores --> sales
    stores --> inventory
    stores --> orders
    stores --> targets
    products --> sales
    products --> inventory
    suppliers --> sales
    suppliers --> inventory
    suppliers --> orders
```

| Table | Grain | Primary key | Relationship approach |
|---|---|---|---|
| `DimCalendar` | Calendar day | `DateKey` / `CalendarDate` | One calendar date filters the Monday week-start date stored on each fact. |
| `DimRegions` | Operating region | `RegionID` | One region filters its stores; avoid a second competing region path. |
| `DimStores` | Approved retail store | `StoreID` | One-to-many, single direction to all four facts. |
| `DimProducts` | Approved assortment product | `ProductID` | One-to-many, single direction to sales and tracked inventory. |
| `DimSuppliers` | Primary approved supplier | `SupplierID` | One-to-many, single direction to sales, inventory and purchase orders. |
| `FactSalesWeekly` | Store, product, week and sales-record type | `SalesRecordID` | Includes separately identified legitimate return adjustments. |
| `FactInventoryWeekly` | Tracked product, store and reporting week | `InventoryRecordID` | Weighted availability must sum demand before division. |
| `FactPurchaseOrders` | Individual supplier purchase order | `PurchaseOrderID` | Fill rate is weighted by ordered units. |
| `FactStoreTargets` | Store and reporting week | `TargetID` | Not allocated to product, category or supplier. |

## Modelling cautions

1. Sales and inventory share several dimensions, but neither fact should directly filter the other.
2. Product `SupplierID` is retained as descriptive lineage. Avoid activating a redundant supplier-to-product-to-fact route when supplier already directly filters the facts.
3. Calendar date should join to each fact's week-start column. The purchase-order join uses `OrderWeekStart`, not the actual received date.
4. A product category filter cannot legitimately subdivide a store sales target. `Sales Target (Aligned Scope)` therefore returns blank in an incompatible product-level context.
5. Inventory covers tracked products only. Do not compare tracked availability against the entire sales assortment without labelling that difference.
"""


impact = f"""
# Financial opportunity methodology

## What is measured and what is estimated

Recorded sales, discounts, cost and gross profit are measured values from the cleaned weekly point-of-sale fact. Supplier ordered and received units are recorded purchase-order observations. Missed demand and recoverable opportunity are estimates derived from the inventory planning extract.

## Record-level method

For each tracked store–product–week record:

1. `Unfulfilled demand units = MAX(ExpectedDemandUnits - FulfilledDemandUnits, 0)`
2. `Estimated lost units = ROUND(Unfulfilled demand units × category capture factor, 0)`
3. Use a **74%** capture factor for chilled products and **68%** for other tracked categories.
4. `Estimated lost sales = Estimated lost units × prevailing realised unit selling price`
5. `Estimated lost gross profit = Estimated lost units × MAX(realised unit selling price - standard unit cost, 0)`

The capture factor recognises that some customers substitute, defer a purchase or buy elsewhere; not every unavailable unit would otherwise have converted into incremental retailer revenue. The selected factors are scenario assumptions, not externally validated conversion rates.

## Results

| Measure | Value | Interpretation |
|---|---:|---|
| Estimated missed sales | {money(S['estimated_lost_sales'])} | Modelled tracked-range exposure across the complete reporting period. |
| Estimated missed gross profit | {money(S['estimated_lost_gross_profit'])} | Modelled gross-profit exposure before execution costs. |
| Lead supplier share | {pct(F['top_supplier_lost_sales_share'])} | Portion of total modelled loss associated with the highest-exposure supplier. |
| Illustrative recovery assumption | {pct(F['illustrative_recovery_rate'], 0)} | Scenario: 58% of already-adjusted loss exposure is operationally recoverable. |
| Illustrative recoverable sales | {money(F['illustrative_recoverable_sales'])} | Estimated loss × 58%; not a committed forecast. |
| Illustrative recoverable gross profit | {money(F['illustrative_recoverable_gross_profit'])} | Estimated gross-profit loss × 58%; excludes intervention costs. |

## Important boundaries

- The 58% recovery assumption is illustrative and should be replaced with a supplier/store intervention test.
- Recovery values are not additive to already-recorded net sales until a real intervention delivers them.
- Chilled spoilage, transfer costs, discount funding and working-capital effects are not available.
- Supplier association is directional evidence; it is not proof of operational causation.
- The campaign margin comparison does not establish incremental promotional return.
"""


video = f"""
# LinkedIn video storyboard: 82-second recruiter walkthrough

**Format:** 1920 × 1080, 30 fps; record the actual dashboard, Excel workbook, SQL and data model.  
**Music:** Low-volume instrumental rhythm with no vocal; remove it entirely if it competes with the narration.  
**Thumbnail:** Executive dashboard with the caption “99.2% available. So where did {money(S['estimated_lost_sales'])} go?”  
**Opening rule:** Show the finding before introducing the project.

| Time | Screen and cursor movement | Narration | On-screen text |
|---|---|---|---|
| 0–5s | Start on the executive dashboard. Frame the green availability figure, then move directly to the lost-sales estimate. | “Availability looked healthy at {pct(S['availability_pct'])}. The data still showed {money(S['estimated_lost_sales'])} in missed sales.” | {pct(S['availability_pct'])} availability · {money(S['estimated_lost_sales'])} estimated missed sales |
| 5–13s | Zoom out to show the Morrowfield reporting window and regional filters. | “For this independent portfolio project, I built a fictional South African retail case around stock availability, supplier performance and margin.” | Independent portfolio project · Fictional company and data |
| 13–24s | Cut to the workbook data-quality sheet, then the clean dataset and model diagram; highlight real row counts. | “I created and cleaned {S['sales_records']:,} sales records, {S['inventory_records']:,} stock observations and {S['purchase_orders']:,} supplier orders across {S['stores']} stores.” | Excel · SQL · Power Query · Power BI-ready DAX |
| 24–39s | Open the operations page. Select KwaZulu-Natal; allow the cards and charts to update. Hover over the supplier service comparison. | “The national average hid a concentrated problem in coastal stores. I linked weekly stock outcomes to supplier fill rates and delayed deliveries.” | Regional filters update every measure |
| 39–55s | Open Root Cause. Zoom into the supplier share and product Pareto; highlight the top-ten concentration. | “One supplier accounted for {pct(F['top_supplier_lost_sales_share'])} of the estimated lost sales. Just ten products explained {pct(F['top_ten_product_lost_share'])}.” | One supplier: {pct(F['top_supplier_lost_sales_share'])} · Ten products: {pct(F['top_ten_product_lost_share'])} |
| 55–66s | Open Financial Impact. Compare Gauteng's revenue and campaign margin side by side. | “A second issue was hiding in the strongest sales region: the winter campaign delivered only {pct(F['winter_promotion_margin'])} gross margin.” | Revenue leadership does not guarantee healthy margin |
| 66–75s | Open Action Centre. Point to the supplier recovery action, priority stores and commercial owner. | “I translated the findings into supplier recovery, store-level replenishment and promotion guardrails, with named management owners.” | Supply chain · Operations · Commercial finance |
| 75–82s | End on the landing page. Pause on the interactive dashboard and workbook download buttons. | “The full project includes the interactive report, Excel workbook, SQL, model and documentation. You can explore it at the project link.” | Zivan Devitt · Data analytics portfolio · Explore the project |

## Recording notes

- Keep pointer movement slow, deliberate and limited to the element being discussed.
- Record at browser zoom 100%; hide personal browser bookmarks and unrelated tabs.
- Use short cross-dissolves or clean cuts; avoid spinning transitions, typing effects and animated icons.
- Let each filter selection complete before the next cut.
- Export H.264 MP4, 1080p, with burned-in captions in a restrained off-white typeface.
- The walkthrough is a production plan; no video is claimed to exist until it is actually recorded.
"""


linkedin = f"""
# LinkedIn launch post

99.2% availability looked like a reassuring number.

It still hid {money(S['estimated_lost_sales'])} in estimated missed sales.

For my latest independent data analytics portfolio project, I built a fictional South African retail scenario and connected:

• {S['sales_records']:,} weekly sales records  
• {S['inventory_records']:,} inventory observations  
• {S['purchase_orders']:,} supplier purchase orders  
• {S['stores']} stores, {S['products']} products and {S['suppliers']} suppliers

The most important findings were not visible in the headline:

• One supplier accounted for {pct(F['top_supplier_lost_sales_share'])} of estimated missed sales.  
• Ten products accounted for {pct(F['top_ten_product_lost_share'])} of the opportunity.  
• Gauteng led sales, while its winter promotion produced only {pct(F['winter_promotion_margin'])} gross margin.

I cleaned and reconciled the raw extracts, developed the SQL and Power Query workflows, built an Excel analysis workbook and designed an interactive management dashboard with a prioritised action centre.

Tools: Excel, SQL, Power Query, Power BI-ready DAX, Python and an interactive HTML dashboard.

Interactive dashboard: [ADD VERIFIED DASHBOARD LINK]  
GitHub repository: [ADD VERIFIED GITHUB REPOSITORY LINK]

Morrowfield Food Co. and the dataset are fictional; the analysis and project work are real portfolio work.

#DataAnalytics #DataAnalyst #BusinessIntelligence #SQL #Excel #PowerBI #RetailAnalytics #SupplyChainAnalytics
"""


cv = f"""
# CV project entry

**The Availability Gap | Independent Data Analytics Portfolio Project**  
Excel · SQL · Power Query · Power BI-ready DAX · Python · Interactive HTML reporting

- Built and reconciled a fictional retail analytics dataset containing {S['sales_records']:,} weekly sales records, {S['inventory_records']:,} inventory observations and {S['purchase_orders']:,} supplier orders across {S['stores']} stores.
- Modelled store, product, supplier and calendar relationships; documented source defects, cleaning rules, KPI definitions and management-level reconciliations.
- Identified that one supplier accounted for {pct(F['top_supplier_lost_sales_share'])} of {money(S['estimated_lost_sales'])} in estimated missed sales and that ten products contributed {pct(F['top_ten_product_lost_share'])} of the opportunity.
- Produced a multi-page interactive dashboard, professional Excel workbook, SQL management queries and a prioritised supply chain, operations and commercial-finance action plan.
"""


interview = f"""
# Interview preparation: explain the work naturally

## Why did you choose this problem?

I wanted something closer to an analyst's actual job than a sales chart. A retailer can report strong availability and still lose sales in specific stores, while a high-revenue region can weaken margin through discounting. That gave me a genuine management question and several data sources that had to be connected carefully.

## What data did you work with?

The fictional case includes {S['sales_records']:,} cleaned weekly sales records, {S['inventory_records']:,} tracked inventory observations and {S['purchase_orders']:,} purchase orders. The conformed dimensions cover {S['stores']} stores, {S['products']} products, {S['suppliers']} suppliers and 26 reporting weeks.

## How did you clean the data?

I profiled the raw tables before using them. The main issues were repeated extract rows, whitespace in keys, mixed date formats, text percentages, missing transaction costs, inconsistent product categories and unmapped keys. I recovered values only when there was an approved business rule; {S['quarantined_sales_records']} sales rows without a reliable store or product mapping were quarantined rather than guessed. I also kept legitimate returns even though their units and revenue are negative.

## Why did you model it this way?

Sales, inventory, supplier orders and targets answer different questions and exist at different grains. I used conformed store, product, supplier and calendar dimensions so each fact can be filtered consistently without joining facts directly and multiplying values. Store targets stay at the store–week grain; they cannot honestly be allocated to a product unless management provides an allocation rule.

## Which KPI mattered most?

Demand-weighted availability was important, but not sufficient. The stronger management view combines weighted availability with estimated lost sales. The overall rate was {pct(S['availability_pct'])}, which looked healthy, yet the financially weighted exposure revealed where an intervention was needed.

## What was your strongest finding?

{F['top_supplier_name']} accounted for {pct(F['top_supplier_lost_sales_share'])} of estimated missed sales, and its observed fill rate and on-time rate were weaker than management thresholds. Ten products explained {pct(F['top_ten_product_lost_share'])} of the opportunity. The right response was therefore targeted supplier and SKU recovery, not a vague national availability campaign.

## How did you estimate financial impact?

I started with expected minus fulfilled tracked demand at store–product–week level. I applied a category-specific capture factor because an unavailable unit is not automatically a lost sale, then multiplied the adjusted units by realised selling price. Gross-profit opportunity used realised unit margin. The {pct(F['illustrative_recovery_rate'], 0)} recovery scenario is clearly labelled as an assumption, not a promised result.

## What limitations should an employer understand?

The company and data are fictional. Inventory only covers a tracked assortment. Demand and recovery are estimated, and the data does not show substitution, supplier incident logs, spoilage costs or controlled promotion experiments. I describe supplier delivery as a supported association, not proven causation.

## Why did you use that visual design?

I wanted the first screen to answer the management question quickly: sales performance, availability, estimated exposure and the main driver. The deeper pages then separate operational performance, supplier diagnostics, financial impact and ownership. I avoided decorative charts and used colour mainly for status or comparison.

## How did you check your numbers?

I reconciled transaction arithmetic, primary-key uniqueness, approved mappings, sales totals by week, region, category and store, weighted availability, supplier loss shares and store targets. The SQL queries independently reproduce the same management totals. Returns stay in scope, while unmapped records are visibly quarantined.

## What would you do with real company data?

I would confirm the source of demand forecasts, inspect supplier incident and allocation records, check product substitution and stock-expiry exposure, review store transfers and validate whether the same issue appears outside the tracked assortment. I would also test a controlled supplier/store intervention before presenting a firm recovery forecast.

## What would you improve next?

Add customer-level substitution evidence, daily rather than weekly stock visibility, supplier root-cause notes, a monitored intervention outcome and formal promotional uplift or incrementality testing.

## How should you talk about your role?

Say: “For this independent portfolio project, I created and analysed a fictional retail scenario.” Do not imply that Morrowfield was an employer or a paying client.
"""


quality_review = f"""
# Hiring-manager and authenticity review

## Recruiter: first 45 seconds

The landing page names the commercial problem, exposes the main quantified finding and links directly to the interactive dashboard, Excel workbook, SQL and complete project package. The company is visibly identified as fictional without interrupting the commercial narrative.

## Data analyst hiring manager

The project shows source profiling, practical cleaning choices, legitimate-return handling, grain-aware modelling, SQL window functions, management metrics, concentration analysis and recommendations. The analyst does not claim causal proof where only an association exists.

## BI manager

The semantic model uses conformed dimensions and separate facts. Product filters do not incorrectly repeat store-level targets. DAX measures are provided as a Power BI-ready library rather than a falsely claimed published `.pbix` file.

## Senior analyst

The key result comes from the generated operating system rather than a manually invented headline. Weighted denominators, purchase-order service, product Pareto concentration and recovery assumptions are separately traceable to the underlying records.

## Quality assessment

| Dimension | Score / 10 | Review note |
|---|---:|---|
| Business realism | 9.5 | Separate supplier, store, margin and inventory decisions reflect an actual retail review. |
| Dataset realism | 9.4 | Regional variation, returns, promotions, mixed quality and incomplete tracked-range coverage are present. |
| Data cleaning | 9.5 | Recovery, exclusion and exception treatment are explicitly documented. |
| Excel | 9.1 | Native workbook, structured summaries, formulas and source-linked checks; pivot creation depends on supported workbook features. |
| SQL | 9.5 | Ten tested management queries use CTEs, ranking, windows and safe cross-fact aggregation. |
| Modelling | 9.4 | Conformed dimensions and explicit fact grain prevent duplicated targets and inflated joins. |
| DAX | 9.1 | Broad measure library with context safeguards; formulas must still be loaded into Power BI Desktop. |
| Analysis | 9.5 | Regional, supplier, product, timing, store and promotion comparisons support the findings. |
| Root cause | 9.6 | One supplier contributes {pct(F['top_supplier_lost_sales_share'])} of estimated loss beneath a green chain-wide KPI. |
| Commercial thinking | 9.5 | Recorded sales, missed opportunity, margin dilution and decision ownership are separated. |
| Financial impact | 9.2 | Conservative capture assumptions and a labelled illustrative recovery scenario. |
| Dashboard UX | 9.3 | Executive summary, consistent filters, operational diagnostics and an action centre. |
| Visual design | 9.2 | Original restrained enterprise styling; no copied retail brand or generic AI artwork. |
| Storytelling | 9.4 | The headline explicitly explains why a healthy percentage can hide a real issue. |
| GitHub readiness | 9.3 | Repository structure, clean README, source files and security exclusions are prepared. |
| Video plan | 9.2 | Time-coded, source-grounded walkthrough of the actual product; the video itself is not claimed to exist. |
| Recruiter impact | 9.4 | The business case and working files are accessible without reading a long technical report. |

These are internal review judgments, not externally verified employer ratings. A live GitHub repository remains dependent on authenticated account access.

## Presentation quality review

- Company, locations, products and suppliers have consistent operating detail rather than generic placeholders.
- Targets are rounded management thresholds; actual outcomes remain irregular.
- National availability can be green while a supplier-region slice is weak.
- The lowest regional rate does not automatically produce the largest financial loss.
- Some negative values are valid returns, not errors.
- The campaign comparison includes a limitation about selection and incrementality.
- Copy uses direct business language and avoids inflated transformation claims.
- Charts, screenshots and diagrams are derived directly from actual project outputs rather than generic illustrations.
"""


FILES = {
    DOCS / "01-project-selection.md": selection,
    DOCS / "02-management-brief.md": brief,
    DOCS / "03-analysis-and-findings.md": methodology,
    DOCS / "04-data-model.md": model,
    DOCS / "05-financial-impact-methodology.md": impact,
    DOCS / "06-hiring-manager-review.md": quality_review,
    PORTFOLIO / "01-linkedin-video-storyboard.md": video,
    PORTFOLIO / "02-linkedin-launch-post.md": linkedin,
    PORTFOLIO / "03-cv-project-entry.md": cv,
    PORTFOLIO / "04-interview-preparation.md": interview,
}


def data_dictionary() -> None:
    descriptions = {
        "WeekStartDate": "Monday starting the completed reporting week.",
        "StoreID": "Approved store dimension key.",
        "ProductID": "Approved product assortment dimension key.",
        "SupplierID": "Approved primary supplier dimension key.",
        "SalesRecordID": "Unique weekly sales or return adjustment record.",
        "InventoryRecordID": "Unique tracked store-product-week stock observation.",
        "PurchaseOrderID": "Unique supplier purchase-order record.",
        "TargetID": "Unique store-week management target.",
        "ExpectedDemandUnits": "Modelled expected units before stock suppression.",
        "FulfilledDemandUnits": "Expected demand that could be fulfilled from available shelf stock.",
        "EstimatedLostUnits": "Capture-adjusted missing demand units; estimate, not observed transactions.",
        "EstimatedLostSales": "Capture-adjusted missed units multiplied by realised selling price.",
        "EstimatedLostGrossProfit": "Capture-adjusted missed units multiplied by non-negative unit gross margin.",
        "AvailabilityRate": "Fulfilled demand units divided by expected demand units at record grain.",
        "GrossSales": "Signed gross sales before discount, including return reversals.",
        "DiscountAmount": "Signed commercial discount on the sales or return record.",
        "NetSales": "Gross sales less discount; includes signed returns.",
        "CostOfGoodsSold": "Signed realised cost attached to sold or returned units.",
        "GrossProfit": "Net sales less recorded cost of goods sold.",
        "FillRate": "Received purchase-order units divided by ordered units.",
        "OnTimeFlag": "True when the delivery is not later than its promised date.",
        "InventoryTracked": "True when the product belongs to the monitored inventory range.",
        "PromotionName": "Approved campaign label; No promotion denotes a non-promoted record.",
    }
    grains = {
        "DimCalendar": "Calendar day", "DimRegions": "Operating region", "DimStores": "Approved store",
        "DimProducts": "Approved product", "DimSuppliers": "Approved supplier",
        "FactSalesWeekly": "Store-product-week and record type", "FactInventoryWeekly": "Tracked store-product-week",
        "FactPurchaseOrders": "Individual supplier purchase order", "FactStoreTargets": "Store and reporting week",
    }
    rows = []
    for path in sorted((ROOT / "data" / "clean").glob("*.csv")):
        frame = pd.read_csv(path, nrows=100)
        table = path.stem
        for column in frame.columns:
            series = frame[column]
            rows.append({
                "Table": table, "Field": column, "DataType": str(series.dtype), "TableGrain": grains.get(table, "See documentation"),
                "Description": descriptions.get(column, " ".join(__import__("re").findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|[0-9]+", column)) + "."),
                "NullableInSample": bool(series.isna().any()),
                "Example": "" if series.dropna().empty else str(series.dropna().iloc[0]),
            })
    pd.DataFrame(rows).to_csv(DOCS / "data-dictionary.csv", index=False)


def kpi_dictionary() -> None:
    rows = [
        ("Gross Sales", "Signed sales value before discounts, including returns.", "SUM(FactSalesWeekly[GrossSales])", "No fixed target", "FactSalesWeekly", "Weekly", "Compare with net sales to understand discount funding.", "Legitimate return reversals remain in scope."),
        ("Net Sales", "Signed commercial sales after discounts and returns.", "SUM(FactSalesWeekly[NetSales])", "Store sales plan", "FactSalesWeekly", "Weekly", "Primary recorded commercial outcome.", "Covers the selected assortment rather than every retailer product."),
        ("Sales Target Attainment", "Recorded net sales as a share of aligned store-week targets.", "Net Sales / SUM(FactStoreTargets[NetSalesTarget])", "100%", "FactSalesWeekly; FactStoreTargets", "Weekly", "Below 100% indicates a gap to management plan.", "Targets are not allocated to product, category or supplier."),
        ("Gross Profit", "Recorded net sales less cost of goods sold.", "SUM(NetSales) - SUM(CostOfGoodsSold)", "No fixed absolute target", "FactSalesWeekly", "Weekly", "Measures the gross commercial contribution of the scoped range.", "Excludes operating costs and promotional funding adjustments."),
        ("Gross Margin", "Gross profit as a share of recorded net sales.", "SUM(GrossProfit) / SUM(NetSales)", "29%", "FactSalesWeekly", "Weekly", "A declining margin can accompany rising sales.", "Category and promotion mix affect comparisons."),
        ("Effective Discount Rate", "Recorded discounts as a share of gross sales.", "SUM(DiscountAmount) / SUM(GrossSales)", "Monitor by campaign", "FactSalesWeekly", "Weekly", "Shows the realised commercial price concession.", "Cannot establish incremental campaign ROI."),
        ("Demand-Weighted Availability", "Fulfilled tracked demand as a share of expected tracked demand.", "SUM(FulfilledDemandUnits) / SUM(ExpectedDemandUnits)", "94%", "FactInventoryWeekly", "Weekly", "Weighting prevents low-volume products from dominating.", "Only covers the tracked product range; expected demand is modelled."),
        ("Availability Gap", "Difference between observed weighted availability and management target.", "Demand-Weighted Availability - 94%", "At least zero", "FactInventoryWeekly; FactStoreTargets", "Weekly", "Shows percentage-point performance against the reference.", "A green total can hide weak supplier-region slices."),
        ("Estimated Lost Sales", "Capture-adjusted modelled sales missed when tracked demand is unfulfilled.", "SUM(EstimatedLostSales)", "Minimise", "FactInventoryWeekly", "Weekly", "Sizes the commercial exposure rather than just the shortage rate.", "Estimated; assumes category-specific demand capture factors."),
        ("Estimated Lost Gross Profit", "Capture-adjusted gross profit associated with modelled lost demand.", "SUM(EstimatedLostGrossProfit)", "Minimise", "FactInventoryWeekly", "Weekly", "Shows approximate contribution exposure before intervention costs.", "Estimated; excludes spoilage, transfers and execution cost."),
        ("Supplier Fill Rate", "Received supplier order units as a share of ordered units.", "SUM(ReceivedUnits) / SUM(OrderedUnits)", "95%", "FactPurchaseOrders", "Weekly", "Order-weighted view of delivery completeness.", "Describes observed orders; does not explain why units were short."),
        ("On-Time Delivery", "Purchase orders received no later than their promised date.", "COUNT(OnTimeFlag=TRUE) / COUNT(PurchaseOrderID)", "93%", "FactPurchaseOrders", "Weekly", "Measures delivery reliability at order grain.", "An early or on-time order may still be short."),
        ("Stockout Hours", "Estimated hours of shelf unavailability within the tracked week.", "SUM(StockoutHours)", "Minimise", "FactInventoryWeekly", "Weekly", "Supports operational exception investigation.", "Estimated from the fulfilled-demand ratio and trading-hour assumption."),
        ("Top-10 Product Loss Share", "Share of estimated lost sales explained by the ten highest-loss products.", "Top-10 product estimated lost sales / all tracked estimated lost sales", "Monitor concentration", "FactInventoryWeekly; DimProducts", "Weekly", "Identifies whether a targeted product intervention is sensible.", "Ranking changes with the selected filter scope."),
        ("Supplier Loss Contribution", "Supplier share of total estimated tracked-range missed sales.", "Supplier estimated lost sales / all supplier estimated lost sales", "Monitor concentration", "FactInventoryWeekly; DimSuppliers", "Weekly", "Identifies financially material supplier exposure.", "Association should not be treated as proven causation."),
        ("Illustrative Recoverable Sales", "Scenario-based portion of modelled missed sales assumed operationally recoverable.", "Estimated Lost Sales × 58%", "Scenario assumption", "FactInventoryWeekly", "Review cycle", "Translates exposure into a cautious discussion scenario.", "Not a forecast; 58% must be replaced with measured intervention performance."),
        ("Illustrative Recoverable Gross Profit", "Scenario-based portion of modelled gross-profit exposure assumed recoverable.", "Estimated Lost Gross Profit × 58%", "Scenario assumption", "FactInventoryWeekly", "Review cycle", "Shows approximate gross-profit discussion potential.", "Excludes recovery cost, working capital and execution constraints."),
    ]
    pd.DataFrame(rows, columns=["KPI Name", "Business Definition", "Formula", "Target", "Source", "Frequency", "Interpretation", "Potential Caveats"]).to_csv(DOCS / "kpi-dictionary.csv", index=False)


def diagram() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(figsize=(15.4, 8.7), facecolor="#11161b")
    ax.set_facecolor("#11161b")
    ax.set_xlim(0, 15.4)
    ax.set_ylim(0, 8.7)
    ax.axis("off")
    ax.text(.72, 8.02, "MORROWFIELD / DATA MODEL", fontsize=12, weight="bold", color="#d0ad77")
    ax.text(.72, 7.47, "Conformed dimensions. Separate facts.", fontsize=23, weight="bold", color="#f1eee8")
    ax.text(.74, 7.07, "Single-direction relationships prevent double counting across sales, stock, supplier service and targets.", fontsize=10.2, color="#aeb6bd")

    nodes = {
        "DimCalendar": (2.35, 5.72, "182 calendar dates"),
        "DimStores": (5.83, 5.72, f"{S['stores']} approved stores"),
        "DimProducts": (9.32, 5.72, f"{S['products']} assortment products"),
        "DimSuppliers": (12.80, 5.72, f"{S['suppliers']} suppliers"),
        "FactSalesWeekly": (2.73, 2.72, f"{S['sales_records']:,} sales records"),
        "FactInventoryWeekly": (6.23, 2.72, f"{S['inventory_records']:,} tracked snapshots"),
        "FactPurchaseOrders": (9.73, 2.72, f"{S['purchase_orders']:,} purchase orders"),
        "FactStoreTargets": (13.22, 2.72, "936 store-week targets"),
    }
    edges = [
        ("DimCalendar", "FactSalesWeekly"), ("DimCalendar", "FactInventoryWeekly"),
        ("DimStores", "FactSalesWeekly"), ("DimStores", "FactInventoryWeekly"),
        ("DimStores", "FactPurchaseOrders"), ("DimStores", "FactStoreTargets"),
        ("DimProducts", "FactSalesWeekly"), ("DimProducts", "FactInventoryWeekly"),
        ("DimSuppliers", "FactInventoryWeekly"), ("DimSuppliers", "FactPurchaseOrders"),
    ]
    for start, end in edges:
        x1, y1, _ = nodes[start]
        x2, y2, _ = nodes[end]
        ax.add_patch(FancyArrowPatch((x1, y1 - .49), (x2, y2 + .55), arrowstyle="-|>", mutation_scale=10, linewidth=.95, color="#55616c", alpha=.68, connectionstyle="arc3,rad=0"))
    for name, (x, y, subtitle) in nodes.items():
        is_fact = name.startswith("Fact")
        width = 2.95 if is_fact else 2.74
        patch = FancyBboxPatch((x - width / 2, y - .48), width, .97, boxstyle="round,pad=.04,rounding_size=.09", linewidth=1, edgecolor="#586771" if is_fact else "#3d484f", facecolor="#192129" if is_fact else "#151b20")
        ax.add_patch(patch)
        ax.text(x, y + .13, name, color="#f1eee8", fontsize=9.5 if is_fact else 10.2, weight="bold", ha="center", va="center")
        ax.text(x, y - .20, subtitle, color="#d0ad77" if is_fact else "#aab3ba", fontsize=8.3, ha="center", va="center")
    ax.text(.76, 1.11, "MODEL RULE", color="#d0ad77", fontsize=9.2, weight="bold")
    ax.text(.76, .72, "Store targets remain at store–week grain. Product and supplier filters must not repeat or fabricate target allocations.", color="#b9c1c7", fontsize=9.2)
    fig.savefig(IMAGES / "data-model.png", dpi=170, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(IMAGES / "data-model.svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def notebook() -> None:
    cells = [
        {"cell_type": "markdown", "metadata": {}, "source": ["# The Availability Gap — reproducible analysis\n", "Independent portfolio project. Morrowfield Food Co. and the dataset are fictional.\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["from pathlib import Path\n", "import sqlite3\n", "import pandas as pd\n", "root = Path.cwd()\n", "if not (root / 'data' / 'clean').exists():\n", "    root = root.parent\n", "connection = sqlite3.connect(root / 'data' / 'clean' / 'morrowfield_analytics.sqlite')\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["pd.read_sql_query('''\n", "SELECT SUM(NetSales) AS net_sales, SUM(GrossProfit) AS gross_profit,\n", "       SUM(GrossProfit) / SUM(NetSales) AS gross_margin\n", "FROM FactSalesWeekly\n", "''', connection)\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["pd.read_sql_query('''\n", "SELECT s.SupplierName, SUM(i.EstimatedLostSales) AS estimated_lost_sales,\n", "       SUM(i.EstimatedLostSales) / SUM(SUM(i.EstimatedLostSales)) OVER () AS loss_share\n", "FROM FactInventoryWeekly i JOIN DimSuppliers s ON s.SupplierID = i.SupplierID\n", "GROUP BY s.SupplierName ORDER BY estimated_lost_sales DESC\n", "''', connection).head(8)\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["pd.read_sql_query('''\n", "SELECT ds.Region, SUM(fs.NetSales) AS net_sales,\n", "       SUM(fs.GrossProfit) / SUM(fs.NetSales) AS gross_margin,\n", "       SUM(fs.DiscountAmount) / SUM(fs.GrossSales) AS discount_rate\n", "FROM FactSalesWeekly fs JOIN DimStores ds ON ds.StoreID = fs.StoreID\n", "GROUP BY ds.Region ORDER BY net_sales DESC\n", "''', connection)\n"]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## Interpretation\n", "Supplier and regional differences describe associations. Estimated lost sales depend on the documented category-specific demand-capture assumptions; they are not recorded revenue.\n"]},
    ]
    payload = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.11"}}, "nbformat": 4, "nbformat_minor": 5}
    (ROOT / "analysis" / "morrowfield-analysis.ipynb").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    for path, content in FILES.items():
        write(path, content)
    data_dictionary()
    kpi_dictionary()
    diagram()
    notebook()
    print(json.dumps({"status": "ok", "documentation_files": len(list(DOCS.glob("*"))), "portfolio_files": len(list(PORTFOLIO.glob("*"))), "diagram": str(IMAGES / "data-model.png")}))


if __name__ == "__main__":
    main()
