# The Availability Gap

**Retail Availability, Supplier Performance & Margin Analysis**

[View the live interactive dashboard](https://zivandevitt-cmd.github.io/the-availability-gap/)

## Project overview

The Availability Gap is an independent data analytics portfolio project built around **Morrowfield Food Co.**, a fictional South African grocery retailer.

The project investigates a commercial problem that is easy to miss in headline reporting: overall product availability can appear healthy while a concentrated supplier, store or product issue still creates meaningful lost-sales and gross-profit exposure.

The analysis connects sales, inventory, supplier orders, stores, products and promotional activity to identify where availability losses originate, quantify their financial impact and translate the findings into management actions.

## Business problem

Management needs to understand:

- Why missed sales exist despite strong overall availability
- Which suppliers, products and stores are driving the opportunity
- How supplier service affects inventory availability
- Where promotional activity is weakening gross margin
- Which actions should be prioritised by supply chain, operations and commercial teams

## Dataset

The connected analytical dataset contains:

- **69,563** sales records
- **52,208** inventory observations
- **5,744** supplier orders
- **36** stores
- **77** products
- **12** suppliers
- Raw and cleaned datasets
- A **15-item data-quality log**

The data is structured as a connected retail operating model: supplier performance affects inventory availability, availability affects sales, and promotional activity affects both revenue and margin.

## Key findings

### 1. Healthy national availability hides concentrated commercial loss

Overall tracked availability is approximately **99.2%**, yet the model identifies approximately **R685.1k in estimated missed sales**.

### 2. One supplier drives most of the availability opportunity

**North Coast Cold Stores contributes approximately 72% of estimated missed sales**, making supplier recovery the primary operational priority.

### 3. The opportunity is highly concentrated by product

The top ten products account for approximately **78.1% of the estimated missed-sales opportunity**, allowing management action to focus on a relatively small number of products.

### 4. Strong revenue does not guarantee healthy margin

**Gauteng produces the strongest revenue**, but aggressive promotional activity weakens profitability. The winter promotion analysed in the project delivered a gross margin of approximately **17.8%**.

## Analytical approach

The project follows the full analyst workflow:

1. Review and clean raw source data
2. Document data-quality issues and business rules
3. Build a connected analytical data model
4. Reconcile core measures across source tables
5. Analyse sales, availability, supplier service and margin
6. Quantify estimated lost-sales and lost-gross-profit opportunity
7. Test findings through SQL management queries
8. Build management reporting in Excel and an interactive HTML dashboard
9. Translate findings into prioritised actions

## Tools and techniques

- **Excel** — structured tables, formulas, reconciliation controls, charts and operational analysis
- **Power Query** — transformation and preparation logic
- **SQL** — management queries, joins, CTEs, window functions, ranking and contribution analysis
- **Power BI-ready DAX** — KPI and analytical measure library
- **Python** — analytical validation and supporting project workflows
- **HTML / JavaScript** — responsive interactive management dashboard

## Excel analyst workbook

The Excel workbook contains **14 working sheets**, including:

- Executive controls
- Supplier-order analysis
- Supplier diagnostics
- Store priorities
- Product Pareto analysis
- Data-quality controls
- Native Excel charts
- Cross-sheet reconciliation

All **eight reconciliation checks passed**.

The workbook is available in the [`excel`](./excel/) folder.

## SQL analysis

Ten management-focused SQL analyses were developed and tested successfully. They cover areas including:

- Overall commercial performance
- Availability loss
- Supplier service
- Product concentration
- Store prioritisation
- Promotional margin
- Period comparison
- Contribution analysis
- Exception detection

SQL files are available in the [`sql`](./sql/) folder.

## Interactive dashboard

The published dashboard contains seven analytical pages:

1. Executive overview
2. Commercial analysis
3. Product analysis
4. Store analysis
5. Root-cause analysis
6. Supplier diagnostics
7. Action centre

Dashboard filters were independently reconciled across region, category and combined-filter scenarios.

Responsive layouts were validated at **1,440 px, 900 px, 600 px and 390 px**.

[Open the live dashboard](https://zivandevitt-cmd.github.io/the-availability-gap/)

## Validation

Completed quality assurance includes:

- Ten SQL management queries executed successfully
- Four independent dashboard filter scenarios reconciled
- Region, category and combined filters validated
- Incompatible store selections cleared when region changes
- Sales targets suppressed when category filters would make them misleading
- Eight Excel reconciliation checks passed
- Responsive layouts tested across desktop, tablet and mobile widths
- No horizontal overflow or duplicated dashboard elements

## Repository structure

```text
the-availability-gap/
│
├── index.html
├── README.md
│
├── excel/
├── data/
│   ├── raw/
│   └── cleaned/
├── sql/
├── power-query/
├── dax/
├── documentation/
└── recruiter/
```

## About the project

**Morrowfield Food Co., its suppliers and the dataset are fictional.**

The project was created as an independent portfolio case study to demonstrate practical data analysis, data cleaning, modelling, SQL, Excel, business intelligence, financial-impact analysis and management communication.

**Zivan Devitt**  
Data Analyst Portfolio
