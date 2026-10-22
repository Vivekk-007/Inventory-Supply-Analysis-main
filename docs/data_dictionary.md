# Data dictionary, metrics, and limitations

## Source profile

`Inventory management dataset.csv` contains 91,250 records and these 15 columns. The extract covers 2024-01-01 to 2024-12-30 (365 distinct dates), with 50 SKUs, 5 warehouses, 10 suppliers, and 4 region labels. There are no nulls or fully duplicated rows. The rows appear to represent SKU/warehouse/date observations, but the extract has no explicit primary key or data-generation notes.

| Field | Observed type | Meaning / use |
| --- | --- | --- |
| `Date` | date text, DMY | Observation date; parse with day-first format |
| `SKU_ID` | identifier | Product key |
| `Warehouse_ID` | identifier | Warehouse key |
| `Supplier_ID` | identifier | Associated supplier as recorded |
| `Region` | category | Region label; check its stability before geographic inference |
| `Units_Sold` | integer | Daily recorded sales quantity |
| `Inventory_Level` | integer | Recorded inventory quantity for that observation |
| `Supplier_Lead_Time_Days` | integer | Lead time in days |
| `Reorder_Point` | integer | Recorded reorder threshold |
| `Order_Quantity` | integer | Recorded order quantity; zero is common |
| `Unit_Cost` | decimal | Unit cost |
| `Unit_Price` | decimal | Unit selling price |
| `Promotion_Flag` | 0/1 | Promotion indicator |
| `Stockout_Flag` | 0/1 | Stockout indicator; zero in every source row |
| `Demand_Forecast` | decimal | Forecast quantity for the observation |

## Measures

- **Revenue** = `Units_Sold × Unit_Price`.
- **Gross profit** = `Units_Sold × (Unit_Price − Unit_Cost)`. This omits logistics, overhead, discounts not captured in price, and other expenses.
- **Forecast error** = `Units_Sold − Demand_Forecast` (positive means under-forecast; negative means over-forecast).
- **MAE** = mean absolute forecast error in units per source row.
- **WAPE** = sum of absolute errors / sum of actual sales. Unlike row-level MAPE, it remains defined when individual rows have zero sales as long as total sales are positive.
- **At/below reorder point** = count of observations where inventory is less than or equal to the supplied reorder point. It is a screening indicator, not a proof of a stockout or missed service target.
- **Estimated days of cover** = inventory on the final date / mean daily sales for that SKU and warehouse across the extract. This is a simple historical-rate proxy, not a forecast or safety-stock policy.
- **Cover below average lead time** = estimated days of cover less than mean recorded lead time. It is an investigation prompt only; it ignores demand variability and the timing/order pipeline.

## Data quality and interpretation limitations

- All `Stockout_Flag` values are 0, so the field has no variation and cannot measure stockout frequency, fill rate, or service level.
- The dates end on December 30 rather than December 31. Avoid claiming a complete calendar year.
- `Region` is not stable within the SKU/warehouse grain: source records assign multiple region labels to a SKU/warehouse across dates. Region aggregates are descriptive of the extract's labels, not reliable warehouse geography.
- `Order_Quantity` can describe order events, but the file has no order ID, order status, receipt date, or backorder field. Do not infer backorders or fulfillment.
- There is no category, transportation cost, or inventory valuation field. Category and transportation-cost analysis shown in the supplied screenshot cannot be reproduced from this CSV.
- Promotions are observational. The higher mean sales on promotion records, if observed, does not establish a causal promotion lift.
- The forecast horizon and method are undocumented. Report accuracy only as retrospective comparison against this extract.
- The daily extract has no opening/closing stock reconciliation or purchase order pipeline. Turnover, inventory availability, and reorder recommendations should be treated as proxies until these data are supplied.
