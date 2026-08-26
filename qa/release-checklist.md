# Release checklist

**Decision:** PASS  
**Review date:** 25 August 2026  
**Weighted release score:** **99.5 / 100**

## Calculation reconciliation

The complete self-contained report was checked in Chromium against independently calculated source controls for four scopes:

1. Complete business: R124,158,834.86 net sales; R685,123.81 estimated missed sales; 69,563 sales records.
2. KwaZulu-Natal: R27,130,099.32 net sales; R315,171.84 estimated missed sales.
3. Chilled Dairy: R27,746,250.28 net sales; R515,730.68 estimated missed sales.
4. KwaZulu-Natal and Chilled Dairy: R6,340,391.87 net sales; R269,319.09 estimated missed sales.

Every tested monetary value, percentage, record count and applicable target matched the independent calculation. Product-category selections correctly suppress store-grain targets instead of allocating unsupported targets to products.

## Browser and interaction checks

- All seven management-report pages were opened and matched their active navigation labels.
- All 17 plotted chart series were matched to their visible legend names, definitions and computed colours.
- Multi-select checkbox states, visible selected counts, active chips and clear-all behaviour passed.
- Region-to-store cascading remained valid when the upstream region changed; incompatible store selections were removed automatically.
- Category-to-supplier cascading removed incompatible supplier selections.
- Supplier selections survived separate search terms and retained visible selected-row status.
- Product tables correctly sorted by estimated missed sales and advanced from rows 1–11 to rows 12–22.
- The complete report passed real-browser layout checks at **1440 × 1000**, **900 × 900**, **600 × 900**, and **390 × 844** pixels, with no document overflow or duplicate element IDs.
- The recruiter landing page was separately verified at desktop width and at a real 390-pixel mobile viewport.
- No report-originated console errors were observed.

The full-data report was used for financial reconciliation and responsive checks. A separate temporary 1,800-row fixture, containing all 36 stores, 77 products, four regions and 12 suppliers and running the identical report code, completed **36** browser interaction and legend checks. That fixture was removed before publication.

## Supporting deliverables

- Excel: 14 of 14 worksheets rendered; eight cross-sheet reconciliation controls passed; no spreadsheet formula errors were found.
- SQL: all 10 management queries executed against the included SQLite database; zero referential-integrity exceptions were returned.
- Packaging: the project archive includes the workbook and dashboard but excludes environment files, Git metadata and workbook inspection intermediates.
- Fictional-business disclosure is present in the recruiter site, report, repository documentation and launch copy.

## Weighted scoring

| Category | Weight | Score | Weighted contribution |
|---|---:|---:|---:|
| Calculation and data accuracy | 30% | 100 | 30.0 |
| Filter and interaction quality | 20% | 100 | 20.0 |
| Page and content completeness | 15% | 100 | 15.0 |
| Technical robustness | 15% | 98 | 14.7 |
| Visual and executive design | 10% | 98 | 9.8 |
| Responsive and accessible use | 10% | 100 | 10.0 |
| **Overall** | **100%** | | **99.5** |

## Known boundaries

The standalone report uses the browser-native `DecompressionStream` API and therefore requires a modern browser. Excel contains reviewed transaction and inventory samples together with full management controls; the complete fact tables are included separately as CSV and SQLite. DAX measures are supplied as a Power BI-ready library, not misrepresented as a published `.pbix` file. Estimated missed sales and recovery scenarios remain modelled opportunities rather than recorded revenue.
