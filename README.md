# Inventory & Supply Chain Planning Analytics

**Author:** Vivek Kumar · [GitHub](https://github.com/Vivekk-007)  
**Focus:** Supply chain planning, inventory optimization, demand analysis, and operational analytics  
**Tools:** Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter, SQL, and Power BI

A planning-focused portfolio project that turns a daily SKU–warehouse extract into demand, forecast accuracy, reorder exposure, inventory coverage, and commercial performance views. It is intended for Supply Chain Planning Intern interviews, operations analysts, and business stakeholders.

> **Source attribution:** This repository was adapted from the existing `Inventory-Supply-Analysis` project ZIP and its accompanying files. Original source author and repository URL were not present in the downloaded files, so they are not guessed here. The source notebook, dashboard, and dataset are retained as project inputs; Vivek Kumar's adaptations are documented in this README and the project materials.

## Implementation plan and current status

1. Profile the supplied data and audit the original notebook and dashboard for reproducibility and valid interpretation. **Complete.**
2. Build a repeatable, planning-oriented Python analysis and usable notebook. **Complete.**
3. Document the data model, decision measures, limitations, and a Power BI rebuild path. **Complete.**
4. Run the analysis and validate its outputs in the available local environment. **Complete; see validation notes below.**
5. Package the work in five logical Git commits. **Complete.**

## Repository contents

| Path | Purpose |
| --- | --- |
| `Inventory management dataset.csv` | Source extract (91,250 daily records) |
| `src/analysis.py` | Validation, derived metrics, and repeatable planning tables |
| `Inventory_Management_EDA.ipynb` | Guided EDA and supply planning analysis notebook |
| `sql/planning_views.sql` | Portable SQL patterns for a staged source table |
| `docs/data_dictionary.md` | Fields, calculations, data quality, and interpretation limits |
| `docs/power_bi_rebuild.md` | PBIX feasibility, data model, measures, and report design |
| `Inventory and Supply Chain Management Analysis.pbix` | Original PBIX source artifact; not rewritten |
| `Inventory & Supply Management Dashboard.png` | Original dashboard screenshot; not a valid preview of this dataset |
| `requirements.txt` | Python dependencies for the notebook and analysis |

## Run locally

From the repository directory, create and activate a virtual environment, then install dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter notebook
```

Open `Inventory_Management_EDA.ipynb` and run all cells from top to bottom. To generate the CSV planning tables from the command line:

```powershell
python src/analysis.py
```

The script reads the source CSV in the repository root and writes reproducible tables to `outputs/` (ignored by Git). You can use `--input` and `--output-dir` to specify alternate paths.

## Findings from the supplied extract

The source has 91,250 rows, 15 columns, 50 SKUs, 5 warehouses, 10 suppliers, and 4 region labels. It contains no missing values or exact duplicate rows. Its observed dates run from **2024-01-01 through 2024-12-30**; it does not contain a record for December 31.

- Total recorded sales are 1,829,979 units; calculated revenue is $33.43M and gross profit is $11.09M. Gross profit here is sales multiplied by unit price less unit cost, before other expenses.
- 5.52% of rows are at or below the recorded reorder point. Treat this as a review queue, not a count of unique shortage events.
- The recorded stockout flag is zero in every row. The dataset cannot support a stockout-rate comparison or service-level conclusion.
- Forecast MAE is about 2.38 units per SKU–warehouse–day; WAPE is about 11.87%. WAPE is used instead of MAPE because 620 rows have zero sales. These metrics assess the provided forecasts; they do not establish future forecast performance.
- The original notebook's `/content/...` path was Colab-specific, its saved outputs were based on 73,130 rows, and its row-level MAPE returned infinity. The notebook has been rebuilt to use the checked-in CSV and explicit zero-demand-safe measures.
- The original screenshot presents categories, backorders, and annual data that are absent from this CSV. Do not use it as evidence for this analysis.

See [data dictionary and limitations](docs/data_dictionary.md) for assumptions and interpretation guidance.

## Power BI

The supplied `.pbix` is a packaged Power BI report, but Power BI Desktop is not available in this environment. The binary model and report layout have therefore not been rewritten. The accompanying screenshot does not match the CSV. See [Power BI rebuild guide](docs/power_bi_rebuild.md) for a data-aligned model and suggested measures before presenting a Power BI dashboard.

## Attribution and contributions

The downloaded project files are treated as upstream source material. This adaptation does not claim original authorship of those files. Vivek Kumar's contributions in this repository are the project framing, source audit, repeatable analysis code, corrected notebook, SQL patterns, documentation, and Power BI rebuild specification. The source author's name and repository URL were not included in the ZIP; add the verified original attribution if those details are available.
