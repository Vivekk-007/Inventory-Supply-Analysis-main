"""Planning focused analysis for the Inventory & Supply Chain Planning Analytics project."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "Date", "SKU_ID", "Warehouse_ID", "Supplier_ID", "Region", "Units_Sold",
    "Inventory_Level", "Supplier_Lead_Time_Days", "Reorder_Point", "Order_Quantity",
    "Unit_Cost", "Unit_Price", "Promotion_Flag", "Stockout_Flag", "Demand_Forecast",
}


def load_data(path: Path) -> pd.DataFrame:
    """Load and validate the source extract without silently dropping records."""
    df = pd.read_csv(path, parse_dates=["Date"], dayfirst=True)
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
    if df[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("Required source fields contain missing values")
    if df.duplicated().any():
        raise ValueError("Source contains fully duplicated rows")
    if (df["Units_Sold"] < 0).any() or (df["Inventory_Level"] < 0).any():
        raise ValueError("Sales and inventory must be non-negative")
    return df.sort_values(["Date", "SKU_ID", "Warehouse_ID"]).reset_index(drop=True)


def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """Add transparent commercial, planning, and forecast measures."""
    out = df.copy()
    out["Revenue"] = out["Units_Sold"] * out["Unit_Price"]
    out["Gross_Profit"] = out["Units_Sold"] * (out["Unit_Price"] - out["Unit_Cost"])
    out["Forecast_Error"] = out["Units_Sold"] - out["Demand_Forecast"]
    out["Absolute_Forecast_Error"] = out["Forecast_Error"].abs()
    out["At_or_Below_Reorder_Point"] = out["Inventory_Level"] <= out["Reorder_Point"]
    out["Zero_Sales_Day"] = out["Units_Sold"] == 0
    return out


def forecast_metrics(df: pd.DataFrame) -> dict[str, float | int]:
    """Return MAE, WAPE, and bias; WAPE avoids undefined row-level zero-sales APE."""
    err = df["Units_Sold"] - df["Demand_Forecast"]
    total_sales = df["Units_Sold"].sum()
    return {
        "MAE_units_per_record": float(err.abs().mean()),
        "WAPE": float(err.abs().sum() / total_sales) if total_sales else float("nan"),
        "Forecast_Bias_units_per_record": float(err.mean()),
        "Zero_Sales_Records": int(df["Units_Sold"].eq(0).sum()),
    }


def build_outputs(df: pd.DataFrame, output_dir: Path) -> dict[str, pd.DataFrame]:
    """Create auditable planning tables; outputs are reproducible from the raw CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    latest = df["Date"].max()
    sku_wh = df.groupby(["SKU_ID", "Warehouse_ID"], as_index=False).agg(
        Supplier_ID=("Supplier_ID", "last"),
        Region_Labels=("Region", "nunique"),
        Period_Units_Sold=("Units_Sold", "sum"),
        Average_Daily_Units=("Units_Sold", "mean"),
        Average_Inventory_Units=("Inventory_Level", "mean"),
        Average_Lead_Time_Days=("Supplier_Lead_Time_Days", "mean"),
        Reorder_Point_Units=("Reorder_Point", "last"),
        At_or_Below_Reorder_Point_Days=("At_or_Below_Reorder_Point", "sum"),
        Observation_Days=("Date", "count"),
    )
    ending = df.loc[df["Date"].eq(latest), ["SKU_ID", "Warehouse_ID", "Inventory_Level"]]
    sku_wh = sku_wh.merge(ending, on=["SKU_ID", "Warehouse_ID"], how="left")
    sku_wh["Estimated_Days_of_Cover"] = np.where(
        sku_wh["Average_Daily_Units"].gt(0),
        sku_wh["Inventory_Level"] / sku_wh["Average_Daily_Units"], np.nan,
    )
    sku_wh["Planning_Attention"] = np.select(
        [sku_wh["Inventory_Level"].le(sku_wh["Reorder_Point_Units"]),
         sku_wh["Estimated_Days_of_Cover"].lt(sku_wh["Average_Lead_Time_Days"])],
        ["At/below reorder point", "Cover below average lead time"], default="Monitor",
    )
    sku_wh = sku_wh.sort_values(
        ["Planning_Attention", "Estimated_Days_of_Cover"], ascending=[True, True]
    )

    monthly = df.assign(Month=df["Date"].dt.to_period("M").astype(str)).groupby(
        "Month", as_index=False
    ).agg(Units_Sold=("Units_Sold", "sum"), Demand_Forecast=("Demand_Forecast", "sum"))
    monthly["Forecast_Error"] = monthly["Units_Sold"] - monthly["Demand_Forecast"]

    region = df.groupby("Region", as_index=False).agg(
        Units_Sold=("Units_Sold", "sum"), Revenue=("Revenue", "sum"),
        Gross_Profit=("Gross_Profit", "sum"), Records=("Date", "count"),
    ).sort_values("Units_Sold", ascending=False)

    for name, table in {"sku_warehouse_planning.csv": sku_wh,
                        "monthly_demand.csv": monthly,
                        "region_summary.csv": region}.items():
        table.to_csv(output_dir / name, index=False)
    return {"sku_warehouse_planning": sku_wh, "monthly_demand": monthly, "region_summary": region}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("Inventory management dataset.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    raw = load_data(args.input)
    df = enrich_data(raw)
    tables = build_outputs(df, args.output_dir)
    print(f"Rows: {len(df):,} | period: {df.Date.min():%Y-%m-%d} to {df.Date.max():%Y-%m-%d}")
    print(f"SKUs: {df.SKU_ID.nunique()} | warehouses: {df.Warehouse_ID.nunique()} | suppliers: {df.Supplier_ID.nunique()}")
    print(f"Revenue: ${df.Revenue.sum():,.2f} | gross profit: ${df.Gross_Profit.sum():,.2f}")
    print(f"Rows at/below reorder point: {df.At_or_Below_Reorder_Point.mean():.1%}")
    print(f"Stockout flag rate: {df.Stockout_Flag.mean():.1%} (flag is zero for every record)")
    print(f"Forecast metrics: {forecast_metrics(df)}")
    print(f"Planning table rows: {len(tables['sku_warehouse_planning']):,}")


if __name__ == "__main__":
    main()
