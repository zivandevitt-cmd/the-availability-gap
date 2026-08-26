-- THE AVAILABILITY GAP | Management questions answered from the cleaned source
-- Engine: SQLite 3.25+ (CTEs and window functions required).
-- Every query deliberately aggregates each fact table before joining across facts.

-- Q01. What is the complete commercial and operational position?
WITH sales AS (
    SELECT COUNT(*) AS sales_records,
           SUM(GrossSales) AS gross_sales,
           SUM(DiscountAmount) AS discount_amount,
           SUM(NetSales) AS net_sales,
           SUM(CostOfGoodsSold) AS cost_of_goods,
           SUM(GrossProfit) AS gross_profit
    FROM FactSalesWeekly
), inventory AS (
    SELECT SUM(ExpectedDemandUnits) AS expected_units,
           SUM(FulfilledDemandUnits) AS fulfilled_units,
           SUM(EstimatedLostSales) AS estimated_lost_sales,
           SUM(EstimatedLostGrossProfit) AS estimated_lost_gp
    FROM FactInventoryWeekly
), targets AS (
    SELECT SUM(NetSalesTarget) AS net_sales_target
    FROM FactStoreTargets
)
SELECT s.sales_records,
       ROUND(s.gross_sales, 2) AS gross_sales,
       ROUND(s.discount_amount, 2) AS discount_amount,
       ROUND(s.net_sales, 2) AS net_sales,
       ROUND(s.gross_profit, 2) AS gross_profit,
       ROUND(s.gross_profit * 1.0 / NULLIF(s.net_sales, 0), 4) AS gross_margin_pct,
       ROUND(s.net_sales * 1.0 / NULLIF(t.net_sales_target, 0), 4) AS target_attainment_pct,
       ROUND(i.fulfilled_units * 1.0 / NULLIF(i.expected_units, 0), 4) AS weighted_availability_pct,
       ROUND(i.estimated_lost_sales, 2) AS estimated_lost_sales,
       ROUND(i.estimated_lost_gp, 2) AS estimated_lost_gross_profit
FROM sales s
CROSS JOIN inventory i
CROSS JOIN targets t;

-- Q02. Which weeks deteriorated, and what does the four-week trend show?
WITH weekly_sales AS (
    SELECT WeekStartDate,
           SUM(NetSales) AS net_sales,
           SUM(GrossProfit) AS gross_profit
    FROM FactSalesWeekly
    GROUP BY WeekStartDate
), weekly_inventory AS (
    SELECT WeekStartDate,
           SUM(FulfilledDemandUnits) * 1.0 / NULLIF(SUM(ExpectedDemandUnits), 0) AS availability_pct,
           SUM(EstimatedLostSales) AS estimated_lost_sales
    FROM FactInventoryWeekly
    GROUP BY WeekStartDate
), combined AS (
    SELECT s.WeekStartDate, s.net_sales, s.gross_profit,
           i.availability_pct, i.estimated_lost_sales
    FROM weekly_sales s
    JOIN weekly_inventory i ON i.WeekStartDate = s.WeekStartDate
)
SELECT WeekStartDate,
       ROUND(net_sales, 2) AS net_sales,
       ROUND(availability_pct, 4) AS availability_pct,
       ROUND(estimated_lost_sales, 2) AS estimated_lost_sales,
       ROUND(net_sales - LAG(net_sales) OVER (ORDER BY WeekStartDate), 2) AS net_sales_change_vs_prior_week,
       ROUND(availability_pct - LAG(availability_pct) OVER (ORDER BY WeekStartDate), 4) AS availability_change_vs_prior_week,
       ROUND(AVG(availability_pct) OVER (
           ORDER BY WeekStartDate ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
       ), 4) AS availability_rolling_four_weeks
FROM combined
ORDER BY WeekStartDate;

-- Q03. Which region creates the greatest loss exposure, and does sales leadership
-- hide a weaker margin or unusually deep discounting?
WITH region_sales AS (
    SELECT ds.Region,
           SUM(fs.NetSales) AS net_sales,
           SUM(fs.GrossProfit) AS gross_profit,
           SUM(fs.GrossSales) AS gross_sales,
           SUM(fs.DiscountAmount) AS discount_amount
    FROM FactSalesWeekly fs
    JOIN DimStores ds ON ds.StoreID = fs.StoreID
    GROUP BY ds.Region
), region_inventory AS (
    SELECT ds.Region,
           SUM(fi.ExpectedDemandUnits) AS expected_units,
           SUM(fi.FulfilledDemandUnits) AS fulfilled_units,
           SUM(fi.EstimatedLostSales) AS estimated_lost_sales
    FROM FactInventoryWeekly fi
    JOIN DimStores ds ON ds.StoreID = fi.StoreID
    GROUP BY ds.Region
)
SELECT s.Region,
       ROUND(s.net_sales, 2) AS net_sales,
       ROUND(s.net_sales * 1.0 / SUM(s.net_sales) OVER (), 4) AS sales_contribution_pct,
       ROUND(s.gross_profit * 1.0 / NULLIF(s.net_sales, 0), 4) AS gross_margin_pct,
       ROUND(s.discount_amount * 1.0 / NULLIF(s.gross_sales, 0), 4) AS effective_discount_pct,
       ROUND(i.fulfilled_units * 1.0 / NULLIF(i.expected_units, 0), 4) AS availability_pct,
       ROUND(i.estimated_lost_sales, 2) AS estimated_lost_sales,
       RANK() OVER (ORDER BY i.estimated_lost_sales DESC) AS loss_exposure_rank
FROM region_sales s
JOIN region_inventory i ON i.Region = s.Region
ORDER BY loss_exposure_rank;

-- Q04. Which suppliers have the strongest observed association with availability
-- loss? Purchase-order and inventory facts are aggregated separately.
WITH order_performance AS (
    SELECT SupplierID,
           COUNT(*) AS purchase_orders,
           SUM(OrderedUnits) AS ordered_units,
           SUM(ReceivedUnits) AS received_units,
           SUM(CASE WHEN DaysLate > 0 THEN 1 ELSE 0 END) AS late_orders
    FROM FactPurchaseOrders
    GROUP BY SupplierID
), supplier_exposure AS (
    SELECT SupplierID,
           SUM(ExpectedDemandUnits) AS expected_units,
           SUM(FulfilledDemandUnits) AS fulfilled_units,
           SUM(EstimatedLostSales) AS estimated_lost_sales,
           SUM(EstimatedLostGrossProfit) AS estimated_lost_gp
    FROM FactInventoryWeekly
    GROUP BY SupplierID
)
SELECT d.SupplierName,
       p.purchase_orders,
       ROUND(p.received_units * 1.0 / NULLIF(p.ordered_units, 0), 4) AS weighted_fill_rate,
       ROUND(1 - p.late_orders * 1.0 / NULLIF(p.purchase_orders, 0), 4) AS on_time_rate,
       ROUND(e.fulfilled_units * 1.0 / NULLIF(e.expected_units, 0), 4) AS availability_pct,
       ROUND(e.estimated_lost_sales, 2) AS estimated_lost_sales,
       ROUND(e.estimated_lost_sales * 1.0 / SUM(e.estimated_lost_sales) OVER (), 4) AS share_of_total_loss,
       ROUND(e.estimated_lost_gp, 2) AS estimated_lost_gross_profit
FROM order_performance p
JOIN supplier_exposure e ON e.SupplierID = p.SupplierID
JOIN DimSuppliers d ON d.SupplierID = p.SupplierID
ORDER BY e.estimated_lost_sales DESC;

-- Q05. How concentrated is the lost-sales opportunity across products?
WITH product_losses AS (
    SELECT p.ProductID,
           p.ProductName,
           p.Category,
           s.SupplierName,
           SUM(i.EstimatedLostSales) AS estimated_lost_sales
    FROM FactInventoryWeekly i
    JOIN DimProducts p ON p.ProductID = i.ProductID
    JOIN DimSuppliers s ON s.SupplierID = i.SupplierID
    GROUP BY p.ProductID, p.ProductName, p.Category, s.SupplierName
), pareto AS (
    SELECT *,
           RANK() OVER (ORDER BY estimated_lost_sales DESC) AS lost_sales_rank,
           estimated_lost_sales * 1.0 / NULLIF(SUM(estimated_lost_sales) OVER (), 0) AS loss_share,
           SUM(estimated_lost_sales) OVER (
               ORDER BY estimated_lost_sales DESC
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) * 1.0 / NULLIF(SUM(estimated_lost_sales) OVER (), 0) AS cumulative_loss_share
    FROM product_losses
)
SELECT lost_sales_rank, ProductName, Category, SupplierName,
       ROUND(estimated_lost_sales, 2) AS estimated_lost_sales,
       ROUND(loss_share, 4) AS loss_share,
       ROUND(cumulative_loss_share, 4) AS cumulative_loss_share
FROM pareto
ORDER BY lost_sales_rank
LIMIT 15;

-- Q06. Which stores should regional teams prioritise first?
WITH store_inventory AS (
    SELECT StoreID,
           SUM(ExpectedDemandUnits) AS expected_units,
           SUM(FulfilledDemandUnits) AS fulfilled_units,
           SUM(EstimatedLostSales) AS estimated_lost_sales,
           SUM(EstimatedLostGrossProfit) AS estimated_lost_gp
    FROM FactInventoryWeekly
    GROUP BY StoreID
), ranked AS (
    SELECT s.Region, s.StoreName, s.StoreFormat,
           i.expected_units, i.fulfilled_units,
           i.estimated_lost_sales, i.estimated_lost_gp,
           RANK() OVER (
               PARTITION BY s.Region ORDER BY i.estimated_lost_sales DESC
           ) AS regional_priority_rank
    FROM store_inventory i
    JOIN DimStores s ON s.StoreID = i.StoreID
)
SELECT Region, StoreName, StoreFormat, regional_priority_rank,
       ROUND(fulfilled_units * 1.0 / NULLIF(expected_units, 0), 4) AS availability_pct,
       ROUND(estimated_lost_sales, 2) AS estimated_lost_sales,
       ROUND(estimated_lost_gp, 2) AS estimated_lost_gross_profit
FROM ranked
WHERE regional_priority_rank <= 3
ORDER BY Region, regional_priority_rank;

-- Q07. When did the most severe supplier-region disruption begin, peak and
-- improve? LAG and LEAD provide adjacent-week context.
WITH supplier_region_weeks AS (
    SELECT i.WeekStartDate, st.Region, su.SupplierName,
           SUM(i.FulfilledDemandUnits) * 1.0 / NULLIF(SUM(i.ExpectedDemandUnits), 0) AS availability_pct,
           SUM(i.EstimatedLostSales) AS estimated_lost_sales
    FROM FactInventoryWeekly i
    JOIN DimStores st ON st.StoreID = i.StoreID
    JOIN DimSuppliers su ON su.SupplierID = i.SupplierID
    WHERE su.SupplierID = 'SUP002'
      AND st.Region IN ('KwaZulu-Natal', 'Eastern Cape')
    GROUP BY i.WeekStartDate, st.Region, su.SupplierName
)
SELECT WeekStartDate, Region, SupplierName,
       ROUND(availability_pct, 4) AS availability_pct,
       ROUND(estimated_lost_sales, 2) AS estimated_lost_sales,
       ROUND(LAG(availability_pct) OVER (
           PARTITION BY Region ORDER BY WeekStartDate
       ), 4) AS prior_week_availability,
       ROUND(LEAD(availability_pct) OVER (
           PARTITION BY Region ORDER BY WeekStartDate
       ), 4) AS next_week_availability,
       CASE
           WHEN availability_pct < .78 THEN 'Immediate intervention'
           WHEN availability_pct < .90 THEN 'High priority'
           ELSE 'Monitor'
       END AS response_band
FROM supplier_region_weeks
ORDER BY WeekStartDate, Region;

-- Q08. Did the Gauteng winter promotion coincide with margin erosion?
-- This is a descriptive comparison, not a causal or incremental-ROI claim.
SELECT st.Region,
       p.Category,
       CASE
           WHEN fs.PromotionName = 'Winter Price Lock' THEN 'Winter Price Lock'
           WHEN fs.PromotionName = 'No promotion' THEN 'No promotion'
           ELSE 'Other promotion'
       END AS promotion_group,
       COUNT(*) AS sales_records,
       ROUND(SUM(fs.NetSales), 2) AS net_sales,
       ROUND(SUM(fs.GrossProfit) * 1.0 / NULLIF(SUM(fs.NetSales), 0), 4) AS gross_margin_pct,
       ROUND(SUM(fs.DiscountAmount) * 1.0 / NULLIF(SUM(fs.GrossSales), 0), 4) AS effective_discount_pct
FROM FactSalesWeekly fs
JOIN DimStores st ON st.StoreID = fs.StoreID
JOIN DimProducts p ON p.ProductID = fs.ProductID
WHERE st.Region = 'Gauteng'
  AND p.Category IN ('Household Care', 'Personal Care')
GROUP BY st.Region, p.Category, promotion_group
ORDER BY p.Category, promotion_group;

-- Q09. How much does each supplier-region combination contribute to the total
-- estimated opportunity? The denominator is the complete tracked scope.
WITH supplier_region AS (
    SELECT st.Region, su.SupplierName,
           SUM(i.EstimatedLostSales) AS estimated_lost_sales,
           SUM(i.EstimatedLostGrossProfit) AS estimated_lost_gp
    FROM FactInventoryWeekly i
    JOIN DimStores st ON st.StoreID = i.StoreID
    JOIN DimSuppliers su ON su.SupplierID = i.SupplierID
    GROUP BY st.Region, su.SupplierName
)
SELECT Region, SupplierName,
       ROUND(estimated_lost_sales, 2) AS estimated_lost_sales,
       ROUND(estimated_lost_gp, 2) AS estimated_lost_gp,
       ROUND(estimated_lost_sales * 1.0 / NULLIF(SUM(estimated_lost_sales) OVER (), 0), 4) AS contribution_to_total,
       DENSE_RANK() OVER (ORDER BY estimated_lost_sales DESC) AS driver_rank
FROM supplier_region
ORDER BY estimated_lost_sales DESC
LIMIT 12;

-- Q10. Which source checks should pass before management sees the report?
SELECT 'Sales primary key duplicates' AS check_name,
       COUNT(*) - COUNT(DISTINCT SalesRecordID) AS exception_count
FROM FactSalesWeekly
UNION ALL
SELECT 'Inventory primary key duplicates',
       COUNT(*) - COUNT(DISTINCT InventoryRecordID)
FROM FactInventoryWeekly
UNION ALL
SELECT 'Unmapped sales stores', COUNT(*)
FROM FactSalesWeekly f LEFT JOIN DimStores s ON s.StoreID = f.StoreID
WHERE s.StoreID IS NULL
UNION ALL
SELECT 'Unmapped sales products', COUNT(*)
FROM FactSalesWeekly f LEFT JOIN DimProducts p ON p.ProductID = f.ProductID
WHERE p.ProductID IS NULL
UNION ALL
SELECT 'Revenue arithmetic mismatches', COUNT(*)
FROM FactSalesWeekly
WHERE ABS(NetSales - (GrossSales - DiscountAmount)) > .011
UNION ALL
SELECT 'Gross-profit arithmetic mismatches', COUNT(*)
FROM FactSalesWeekly
WHERE ABS(GrossProfit - (NetSales - CostOfGoodsSold)) > .011;

