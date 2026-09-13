# Product-recommendation-engine
# Signal Product Recommendation Engine

A local content-based recommendation engine built with Python and Flask. It uses TF-IDF-style weighting over product names, descriptions, categories, features, brands, and colors, then ranks products with cosine similarity.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000.

## API

- `GET /api/catalog` returns the catalog and available categories.
- `GET /api/recommendations?q=wireless+audio&category=Audio&limit=6` returns ranked products.
- `GET /api/products/<id>` returns one product.

The product catalog lives in `data/products.json`. Replace it with your own records using the same fields to personalize the model.
