# Management assignment: availability and margin recovery

**Issued by:** Head of Retail Operations, Morrowfield Food Co.  
**Analyst:** Zivan Devitt, independent portfolio scenario  
**Reporting window:** 23 February to 23 August 2026, 26 completed trading weeks  
**Decision forum:** Weekly retail performance and supplier recovery meeting

## Company background and operating model

Morrowfield Food Co. is a fictional South African food and household retailer with 36 branches across Gauteng, Western Cape, KwaZulu-Natal and Eastern Cape. Stores trade as neighbourhood markets, conventional markets and larger food halls. This assignment covers a defined 77-product assortment across six trading categories. Supplier purchase orders, weekly point-of-sale extracts, a tracked inventory range and store-level sales targets arrive from separate operational systems.

The extract represents a focused analytical assortment, not the retailer's entire stock-keeping universe. Weekly sales records are store–product observations with separately identified return adjustments. Inventory is available only for products designated as tracked.

## Current business concern

Recorded net sales are R124.16m, equivalent to 96.7% of the store-level sales plan. Demand-weighted availability across the tracked range is 99.2%; viewed on its own, that is above the 94% target. Management still suspects that delivery exceptions and deep promotions are creating preventable commercial gaps in particular stores and categories.

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
| Weekly point-of-sale fact | Store, product, week and record type | 69,563 clean rows | Sales, discounts, returns, cost and gross profit |
| Weekly inventory fact | Tracked store, product and week | 52,208 clean rows | Demand, fulfilment, stockout exposure and estimated loss |
| Supplier purchase orders | Individual supplier order | 5,744 orders | Fill rate, delayed deliveries and supplier service |
| Store targets | Store and week | 936 target rows | Sales plan and operating thresholds |
| Conformed dimensions | Store, product, supplier, region and date | 36 stores; 77 products; 12 suppliers | Consistent filtering and reporting |

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
