# Inventory & Supply Chain Planning Analytics

**Owner:** Vivek Kumar

**GitHub:** [Vivekk-007](https://github.com/Vivekk-007)

**Repository name:** `inventory-supply-chain-planning-analytics`

A reproducible analysis of daily inventory, sales, forecast, supplier lead-time, and reorder-point records. The project uses Python and SQL to create planning review tables and explain how the available evidence can support inventory decisions. It is designed as a portfolio project for supply chain planning, inventory analytics, and operational decision support.

## Contents

- [Project overview](#project-overview)
- [Business problem and objectives](#business-problem-and-objectives)
- [Capabilities and technology](#capabilities-and-technology)
- [Repository structure](#repository-structure)
- [Dataset](#dataset)
- [Data preparation and exploratory analysis](#data-preparation-and-exploratory-analysis)
- [Measures and assumptions](#measures-and-assumptions)
- [Findings and recommendations](#findings-and-recommendations)
- [Power BI files](#power-bi-files)
- [Setup and usage](#setup-and-usage)
- [Validation](#validation)
- [Limitations and future work](#limitations-and-future-work)
- [Author](#author)
- [Source attribution and licensing](#source-attribution-and-licensing)

## Project overview

This project analyzes a daily extract at the SKU, warehouse, and date level. It validates the source data, calculates forecast and commercial measures, and produces planning review tables that help an analyst investigate inventory at or below the recorded reorder point and compare estimated days of cover with recorded supplier lead time.

The work is exploratory decision support. It does not automatically create purchase orders, claim an optimal inventory policy, or measure customer service performance. The meaning and limitations of each measure are documented so findings can be reviewed before operational use.

## Business problem and objectives

Inventory planners need to balance product availability against the cost of holding stock. They also need to understand forecast error, replenishment thresholds, and lead-time exposure. A useful planning review starts with consistent data and clear measures; it should distinguish a signal that needs investigation from a verified shortage or service failure.

Project objectives:

1. Profile the supplied extract and validate its expected fields and record quality.
2. Compare actual sales with the supplied demand forecast using zero-demand-safe measures.
3. Surface SKU-warehouse observations at or below their recorded reorder point.
4. Provide a clearly qualified inventory-cover proxy for prioritizing review.
5. Quantify recorded sales revenue and gross profit from the unit values provided.
6. Document what additional data is needed for service-level, backorder, capacity, and transportation analysis.

## Capabilities and technology

| Area | Implementation |
| --- | --- |
| Data preparation | Python, Pandas, and NumPy |
| Exploratory analysis | Jupyter Notebook, Matplotlib, and Seaborn |
| Planning outputs | Python script generating monthly, regional-label, and SKU-warehouse CSV summaries |
| SQL examples | Aggregation, window functions, reorder review, and WAPE in `sql/planning_views.sql` |
| BI handoff | Power BI source files retained with a data-aligned rebuild guide; the supplied report has not been rewritten |
| Business domain | Supply chain planning, inventory analytics, inventory optimization, and operational decision support |

## Repository structure

```text
.
|-- .gitignore
|-- README.md
|-- Inventory management dataset.csv
|-- Inventory_Management_EDA.ipynb
|-- Inventory and Supply Chain Management Analysis.pbix
|-- Inventory & Supply Management Dashboard.png
|-- requirements.txt
|-- src/
|   `-- analysis.py
|-- sql/
|   `-- planning_views.sql
`-- docs/
    |-- data_dictionary.md
    `-- power_bi_rebuild.md
```

Running the analysis script creates an ignored `outputs/` directory containing generated CSV summaries.

## Dataset

The [source CSV](Inventory%20management%20dataset.csv) contains **91,250 rows** and **15 columns**. It has 365 distinct dates, from 2024-01-01 through 2024-12-30, and represents 50 SKUs across 5 warehouses. Each of the 250 SKU-warehouse combinations has 365 observations. The source has no missing values or fully duplicated rows. There is no December 31 observation.

The original date field is text in day-month-year form and is parsed as a date by the analysis script. The four identifier/category fields are text. Seven quantity and flag fields are integers, while unit cost, unit price, and demand forecast are decimals.

| Column | Type after parsing | Available meaning |
| --- | --- | --- |
| `Date` | Date | Observation date; source text is DD-MM-YYYY |
| `SKU_ID` | Text identifier | SKU key |
| `Warehouse_ID` | Text identifier | Warehouse key |
| `Supplier_ID` | Text identifier | Supplier label associated with the SKU-warehouse record |
| `Region` | Text category | Region label recorded on each row; unstable within a SKU-warehouse over time |
| `Units_Sold` | Integer | Recorded units sold for the day |
| `Inventory_Level` | Integer | Recorded inventory quantity for the day |
| `Supplier_Lead_Time_Days` | Integer | Recorded lead time in days |
| `Reorder_Point` | Integer | Recorded reorder threshold in units |
| `Order_Quantity` | Integer | Daily order quantity field; no order identifier or status is supplied |
| `Unit_Cost` | Decimal | Cost per unit |
| `Unit_Price` | Decimal | Selling price per unit |
| `Promotion_Flag` | Integer flag (0/1) | Promotion indicator |
| `Stockout_Flag` | Integer flag (0/1) | Stockout indicator; zero in every row |
| `Demand_Forecast` | Decimal | Forecast units for the row; forecast horizon and method are undocumented |

For exact field definitions and caveats, see the [data dictionary](docs/data_dictionary.md).

## Data preparation and exploratory analysis

`src/analysis.py` reads the CSV with day-first date parsing and checks the required columns, missing values, duplicate rows, and non-negative sales and inventory. It fails with an error if required data-quality checks do not pass; it does not silently drop or impute records. The validated data is sorted by date, SKU, and warehouse before derived measures are added.

The notebook and script cover:

- Record counts, date coverage, column types, missing values, duplicates, and identifier counts.
- Monthly actual demand compared with the supplied forecast.
- Forecast error, MAE, WAPE, and forecast bias.
- Inventory observations at or below the recorded reorder point.
- Latest inventory and a historical-rate estimate of days of cover by SKU and warehouse.
- Revenue and gross profit derived from sales, unit price, and unit cost.
- Exploratory comparisons by promotion flag and the region labels recorded in the file.

Region labels vary within every SKU-warehouse combination in this extract. Region aggregations are included as summaries of the labels as supplied, not as reliable geographic or warehouse comparisons. Promotion comparisons are observational and do not measure causal lift.

## Measures and assumptions

All row-level measures use one source record per SKU-warehouse-day.

| Measure | Definition | Interpretation |
| --- | --- | --- |
| Revenue | `Units_Sold * Unit_Price` | Sales value from the recorded price; does not adjust for discounts or returns not represented in the source |
| Gross profit | `Units_Sold * (Unit_Price - Unit_Cost)` | Product gross profit before freight, labor, overhead, and other expenses |
| Forecast error | `Units_Sold - Demand_Forecast` | Positive means actual sales exceeded forecast; negative means the forecast exceeded actual sales |
| MAE | `mean(abs(Forecast error))` | Average absolute error in units per source record |
| WAPE | `sum(abs(Forecast error)) / sum(Units_Sold)` | Aggregate absolute error relative to total actual units; defined here despite 620 zero-sales records |
| Mean forecast bias | `mean(Forecast error)` | Positive indicates average under-forecast; negative indicates average over-forecast |
| At/below reorder rate | `count(Inventory_Level <= Reorder_Point) / record count` | Share of daily observations that merit review; not a stockout or a count of distinct shortage events |
| Estimated days of cover | `latest Inventory_Level / mean daily Units_Sold` for each SKU-warehouse | Historical-rate screening proxy over the observed period; not a replenishment recommendation |
| Cover below recorded lead time | `Estimated days of cover < mean Supplier_Lead_Time_Days` | Review signal only; ignores demand variability, safety stock, receipts, and open orders |

The analysis does not calculate inventory turnover, days sales of inventory, warehouse utilization, or a service level. Those measures need valuation, capacity, or fulfillment evidence that this CSV does not contain.

### Cost, supplier, warehouse, and backorder scope

The file supports product-level revenue and gross-profit calculations because it contains units sold, unit price, and unit cost. It has no freight or transportation cost field, so logistics cost analysis is not supported.

Supplier IDs and lead-time values are present. Their recorded mean lead times range from 6.96 days for `SUP_5` to 8.64 days for `SUP_4`. These are averages of repeated daily records, not a sample of independently identified purchase orders or actual-versus-promised delivery measurements; they should not be treated as a supplier scorecard.

Warehouse IDs support SKU-warehouse inventory and demand summaries. The data contains no storage capacity, location, or space utilization field, so warehouse utilization cannot be measured. The `Order_Quantity` field has no order ID, order status, or receipt date. Backorders, fill rate, and order fulfillment cannot be derived.

## Findings and recommendations

The calculations below are from the checked-in CSV and the implemented formulas:

- **Data coverage:** 91,250 records, 250 complete SKU-warehouse series, 50 SKUs, 5 warehouses, 10 suppliers, and 4 region labels. Coverage runs from January 1 to December 30, 2024; do not describe it as a complete calendar-year extract.
- **Demand and forecast:** 1,829,979 units were recorded. MAE is **2.38 units per row** and WAPE is **11.87%**. There are 620 zero-sales rows, which make row-level MAPE unsuitable. Forecast method and horizon are not documented.
- **Reorder review:** 5,041 of 91,250 rows (**5.52%**) are at or below the supplied reorder point. On December 30, 14 of 250 SKU-warehouse records are at or below that threshold. These are observations to investigate, not confirmed stockouts.
- **Availability:** `Stockout_Flag` is zero in all 91,250 rows. This field cannot establish a stockout rate or service level.
- **Commercial value:** calculated revenue is **$33,426,337.22** and calculated gross profit is **$11,088,201.23**, before non-product costs.
- **Monthly demand:** recorded sales peak in March at 231,596 units and are lowest in September at 76,304 units. A single partial year is insufficient to establish a recurring seasonal pattern.
- **Lead time:** mean recorded lead time across rows is 7.98 days, with a range of 2 to 14 days. Supplier-level averages are descriptive only because transactional delivery records are absent.
- **Dimension quality:** every SKU-warehouse combination is associated with all four region labels over the period. Do not use `Region` to infer fixed warehouse geography.

Recommended planning follow-up:

1. Review the 14 end-of-period SKU-warehouse records at or below reorder point against current on-hand stock, open purchase orders, and the actual replenishment policy before taking action.
2. Check the higher-error SKU-warehouse series and validate the forecast horizon, model, and forecast snapshot dates before changing demand plans.
3. Compare recorded lead times with purchase-order and receipt dates before drawing supplier performance conclusions.
4. Correct the changing region mapping and add product and warehouse master data before producing geographic or category-level recommendations.
5. Add stockout, backorder, order-status, receipt, capacity, and transportation-cost data to support service and logistics KPIs.

## Power BI files

The repository includes the supplied [Power BI report](Inventory%20and%20Supply%20Chain%20Management%20Analysis.pbix) and its [screenshot](Inventory%20%26%20Supply%20Management%20Dashboard.png). The PBIX has not been edited or verified in Power BI Desktop. The screenshot is an **original supplied dashboard preview**, not a result of this analysis. Its category, transportation-cost, backorder, warehouse-utilization, and multi-year visuals are not supported by the CSV.

![Original supplied dashboard screenshot; it does not represent the checked-in CSV analysis](Inventory%20%26%20Supply%20Management%20Dashboard.png)

To inspect the supplied report, open the PBIX in Power BI Desktop. To build a report that matches this analysis, import the CSV, set `Date` to a date type, verify the SKU and warehouse grain, and use only measures supported by the source fields. The [Power BI rebuild guide](docs/power_bi_rebuild.md) includes a suggested model and example DAX measures. Do not present the supplied screenshot as a current dashboard for this dataset.

## Setup and usage

### Windows setup

In PowerShell, from the repository directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If script activation is restricted by local PowerShell policy, run the environment's Python executable directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Run the Jupyter notebook

From the repository root, after installing requirements:

```powershell
jupyter notebook Inventory_Management_EDA.ipynb
```

Run the cells in order. The notebook expects the source CSV in the repository root and writes planning summaries under `outputs/`.

### Run the Python analysis

```powershell
python src\analysis.py
```

Optional input and output paths can be supplied as arguments:

```powershell
python src\analysis.py --input "Inventory management dataset.csv" --output-dir outputs
```

The script creates:

- `outputs/sku_warehouse_planning.csv`
- `outputs/monthly_demand.csv`
- `outputs/region_summary.csv`

The generated `outputs/` directory is excluded from Git.

### SQL examples

`sql/planning_views.sql` contains SQL examples for daily demand and forecast error, SKU-warehouse planning review, and aggregate WAPE. Load the CSV into a table named `inventory_daily` and normalize `Date` to a database date type before running the queries. Adjust syntax if required by your database engine.

## Validation

There is no automated test suite in this repository. The analysis script performs input validation when run. In the inspected environment, `python src/analysis.py` completed and generated all three outputs; the SQL examples were also executed against the CSV loaded into SQLite. Re-run the script after changing the input and review its printed row count, date range, metrics, and generated tables.

## Limitations and future work

The results are limited by the fields and coverage in the supplied extract:

- The date series ends on December 30, 2024, and contains only one year of observations.
- The stockout flag has no variation; service level, stockout rate, and backorders are not measurable.
- Region is inconsistent within each SKU-warehouse combination, and no product category is supplied.
- There are no purchase-order IDs, promised/actual receipt dates, order statuses, open order balances, or supplier master attributes.
- There is no warehouse capacity, freight cost, inventory valuation, or expense data.
- Forecast horizon and method are unknown; retrospective error is not a forecast validation design.
- Inventory cover is a simple historical average-rate proxy and omits demand variability, safety stock, and pipeline inventory.
- The promotion flag supports a descriptive comparison only, not causal analysis.

Future work should add validated master data, order and receipt history, inventory valuation and capacity, stockout and fulfillment events, and a forecast evaluation window with documented horizons. With those inputs, the analysis could support lead-time variability, service-level, value-based turnover, and more defensible replenishment policies. The Power BI report should then be rebuilt and reviewed against the validated model.

## Author

**Vivek Kumar**

GitHub: [Vivekk-007](https://github.com/Vivekk-007)

## Source attribution and licensing

This repository adapts files from the upstream [Inventory-Supply-Management_Analytics project](https://github.com/stevenadar/Inventory-Supply-Management_Analytics). The adaptation adds the planning-oriented Python analysis, updated notebook, SQL examples, data-quality documentation, and Power BI rebuild guidance. The upstream dataset, PBIX, and screenshot remain source materials; this project does not claim to have created those assets.

No license file was present in the supplied source files or this repository at review time. No license is asserted here. Review the upstream repository and obtain clarification from its maintainer before redistributing inherited assets.

## Conclusion

This project demonstrates a practical planning workflow: validate operational data, quantify forecast and reorder signals, make assumptions visible, and identify the master and transaction data needed for stronger decisions. Those are core analytical habits for supply chain planning and inventory operations.
