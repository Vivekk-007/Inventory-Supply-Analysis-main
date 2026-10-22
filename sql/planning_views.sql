-- Portable SQL patterns. Load the CSV to a table named inventory_daily first.
-- Date parsing varies by database; normalize Date to DATE during ingestion.

-- Daily demand and retrospective forecast error
SELECT
    Date,
    SUM(Units_Sold) AS actual_units,
    SUM(Demand_Forecast) AS forecast_units,
    SUM(Units_Sold - Demand_Forecast) AS signed_error_units,
    SUM(ABS(Units_Sold - Demand_Forecast)) AS absolute_error_units
FROM inventory_daily
GROUP BY Date
ORDER BY Date;

-- SKU/warehouse planning review. Coverage uses historical average daily sales.
WITH sku_warehouse AS (
    SELECT
        SKU_ID,
        Warehouse_ID,
        MAX(Date) AS last_observed_date,
        AVG(Units_Sold) AS average_daily_units,
        AVG(Supplier_Lead_Time_Days) AS average_lead_time_days,
        MAX(Reorder_Point) AS recorded_reorder_point
    FROM inventory_daily
    GROUP BY SKU_ID, Warehouse_ID
), latest_inventory AS (
    SELECT SKU_ID, Warehouse_ID, Inventory_Level
    FROM (
        SELECT *, ROW_NUMBER() OVER (
            PARTITION BY SKU_ID, Warehouse_ID ORDER BY Date DESC
        ) AS row_number
        FROM inventory_daily
    ) ranked
    WHERE row_number = 1
)
SELECT
    s.SKU_ID,
    s.Warehouse_ID,
    i.Inventory_Level AS latest_inventory,
    s.recorded_reorder_point,
    CASE WHEN i.Inventory_Level <= s.recorded_reorder_point THEN 1 ELSE 0 END AS at_or_below_reorder_point,
    i.Inventory_Level / NULLIF(s.average_daily_units, 0) AS estimated_days_of_cover,
    s.average_lead_time_days
FROM sku_warehouse s
JOIN latest_inventory i
  ON i.SKU_ID = s.SKU_ID
 AND i.Warehouse_ID = s.Warehouse_ID
ORDER BY at_or_below_reorder_point DESC, estimated_days_of_cover;

-- Aggregate WAPE; avoid averaging row-level percentage errors when actuals may be zero.
SELECT
    SUM(ABS(Units_Sold - Demand_Forecast)) / NULLIF(SUM(Units_Sold), 0) AS wape
FROM inventory_daily;
