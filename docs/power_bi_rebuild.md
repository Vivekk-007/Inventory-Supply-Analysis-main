# Power BI rebuild guide

## Current artifact status

`Inventory and Supply Chain Management Analysis.pbix` is a ZIP-packaged Power BI report with a model and report layout. The environment has no Power BI Desktop executable or supported PBIX authoring tooling. Editing the report binary programmatically here is not feasible, so the PBIX is preserved unchanged as upstream material.

The supplied `Inventory & Supply Management Dashboard.png` was reviewed. Its category, transportation-cost, backorder, and annual 2020–2024 visuals do not map to the supplied CSV, which has no category, transportation cost, order status, or backorder fields and only dates in 2024. It should not be presented as the output of this analysis. Rebuild and export a new report in Power BI Desktop before using a dashboard screenshot in an interview portfolio.

## Suggested report model

Load the CSV as a fact table named `InventoryDaily`, at one row per SKU–warehouse–date in this extract. Create a calendar table and relate `Calendar[Date]` one-to-many to `InventoryDaily[Date]`. Add SKU, warehouse, and supplier dimensions only after validating their mapping stability. Do not treat the changing `Region` values as a warehouse dimension. There is no product category dimension in the source.

Suggested page title: **Inventory & Supply Chain Planning Analytics**. Use a restrained KPI row and charts that map directly to the source fields:

1. KPI cards: Units Sold, Revenue, Gross Profit, Forecast WAPE, and rows at/below reorder point.
2. Monthly actual units and demand forecast line chart.
3. SKU–warehouse planning table with ending inventory, reorder point, estimated days of cover, lead time, and attention label.
4. Supplier lead time by supplier and inventory exposure by warehouse, only after key mappings are checked.
5. Region view can be included only with a visible note that region labels vary within SKU/warehouse over time.

Avoid stockout and backorder cards: the stockout flag is always zero, and there is no backorder or order-status field.

## Example DAX measures

```DAX
Units Sold = SUM(InventoryDaily[Units_Sold])
Revenue = SUMX(InventoryDaily, InventoryDaily[Units_Sold] * InventoryDaily[Unit_Price])
Gross Profit = SUMX(InventoryDaily, InventoryDaily[Units_Sold] * (InventoryDaily[Unit_Price] - InventoryDaily[Unit_Cost]))
Absolute Forecast Error = SUMX(InventoryDaily, ABS(InventoryDaily[Units_Sold] - InventoryDaily[Demand_Forecast]))
Forecast WAPE = DIVIDE([Absolute Forecast Error], [Units Sold])
Rows At or Below Reorder Point = CALCULATE(COUNTROWS(InventoryDaily), FILTER(InventoryDaily, InventoryDaily[Inventory_Level] <= InventoryDaily[Reorder_Point]))
Reorder Review Rate = DIVIDE([Rows At or Below Reorder Point], COUNTROWS(InventoryDaily))
```

Use MAE as an average at the row grain, and label its units. Define days-of-cover carefully at SKU/warehouse level using latest stock and a selected historical or forecast demand window; the simple Python proxy in this project uses the full observed period and is not a DAX policy recommendation.
