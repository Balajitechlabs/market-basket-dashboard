# Market Basket Analysis Dashboard

A beginner-friendly Streamlit dashboard demonstrating **Apriori** and **FP-Growth** on transaction baskets.

## Features
- Four built-in sample datasets
- Upload CSV and Excel files
- Apriori, FP-Growth, or compare both
- Support, confidence, and lift controls
- Frequent itemset tables and charts
- Association rules and CSV downloads
- Simplified frequency-ordered FP-tree illustration
- Measured execution times

## Setup
Install Python 3.10 or newer.

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies and launch:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Upload format
Choose one of the two formats in the sidebar:

1. **Products across columns:** each row is one transaction and each non-empty cell is a product.
2. **TransactionID + Item rows:** each row is one product within a transaction. Use columns such as `TransactionID` and `Item` (also accepts common variants like `OrderID` and `Product`).

For supermarket sales exports with one line per sold product, use long format and select the transaction/order ID and product columns. The current long-format reader detects common column names.

## Metric definitions
- **Support:** number of transactions containing the itemset divided by total transactions.
- **Confidence:** support(A and B) divided by support(A), for a rule A → B.
- **Lift:** confidence(A → B) divided by support(B). Lift above 1 suggests a positive association.

## Permanent deployment
This project is ready for a managed deployment using Docker.

### Option 1: Render
1. Push this project to a GitHub repository.
2. Sign in to Render and create a new Web Service from that repository.
3. Choose the repository and keep the default Docker build.
4. Render will build from the included `Dockerfile` and expose the app on port `8501`.

### Option 2: Streamlit Community Cloud
1. Push this repo to GitHub.
2. Log in to Streamlit Community Cloud.
3. Create a new app and select this repository.
4. Set the main file to `app.py`.

### Option 3: Docker locally
```bash
docker build -t market-basket-dashboard .
docker run -p 8501:8501 market-basket-dashboard
```

## Notes
- The example datasets are illustrative sample data, not real sales records.
- The FP-tree chart is a simplified educational prefix-tree illustration. The frequent itemsets and rules are computed using `mlxtend`'s Apriori and FP-Growth implementations.
