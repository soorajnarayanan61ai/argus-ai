# ARGUS AI - Enterprise Data Analyst Platform

ARGUS AI is an enterprise-grade AI Data Analyst Platform built with Python 3.13+, Streamlit, SQLAlchemy, Pandas, DuckDB, Scikit-Learn, and Plotly.

## System Architecture

The project features a pluggable, modular engine architecture:

- **`config/`**: Central YAML and Environment Settings Manager singleton.
- **`core/`**: Core infrastructure including Database abstraction, Logger manager, Session manager, Theme provider, Exception boundary, and Plugin Manager.
- **`services/`**: Independent backend engines:
  1. `file_service.py`: Universal File Loader (CSV, Excel, JSON, XML, PDF, Docx, Pptx, ZIP, Images).
  2. `db_service.py`: Multi-Database Connectors (SQLite, DuckDB, Postgres, MySQL, MSSQL, Oracle, Snowflake, BigQuery).
  3. `ocr_service.py`: OCR Document & Invoice Table Extractor.
  4. `cleaning_service.py`: Data Cleaning & Imputation Engine.
  5. `profiling_service.py`: Data Profiling & Data Quality Score (0-100%).
  6. `analytics_service.py`: Forecasting, ABC Analysis, Pareto 80/20, RFM Customer Segmentation.
  7. `visualization_service.py`: Interactive Plotly Suite & Dashboard Builder.
- **`modules/`**: Pluggable frontend UI views inheriting from `BaseModule`.
- **`utils/`**: General formatting and security utilities.
- **`tests/`**: Automated unit test suite.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit App
streamlit run app.py

# Run Tests
python -m unittest discover -s tests -p "test_*.py"
```

Developed for Enterprise Data Analytics.
