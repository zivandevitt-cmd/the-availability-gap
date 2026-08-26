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
| Estimated missed sales | R685.1k | Modelled tracked-range exposure across the complete reporting period. |
| Estimated missed gross profit | R149.5k | Modelled gross-profit exposure before execution costs. |
| Lead supplier share | 72.0% | Portion of total modelled loss associated with the highest-exposure supplier. |
| Illustrative recovery assumption | 58% | Scenario: 58% of already-adjusted loss exposure is operationally recoverable. |
| Illustrative recoverable sales | R397.4k | Estimated loss × 58%; not a committed forecast. |
| Illustrative recoverable gross profit | R86.7k | Estimated gross-profit loss × 58%; excludes intervention costs. |

## Important boundaries

- The 58% recovery assumption is illustrative and should be replaced with a supplier/store intervention test.
- Recovery values are not additive to already-recorded net sales until a real intervention delivers them.
- Chilled spoilage, transfer costs, discount funding and working-capital effects are not available.
- Supplier association is directional evidence; it is not proof of operational causation.
- The campaign margin comparison does not establish incremental promotional return.
