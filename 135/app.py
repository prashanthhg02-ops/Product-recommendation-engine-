from pathlib import Path

from flask import Flask, jsonify, render_template, request

from recommender import ProductRecommender


BASE_DIR = Path(__file__).parent
app = Flask(__name__, static_folder="static", template_folder="static")
engine = ProductRecommender(BASE_DIR / "data" / "products.json")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/catalog")
def catalog():
    return jsonify({"products": engine.products, "categories": engine.categories()})


@app.get("/api/recommendations")
def recommendations():
    query = request.args.get("q", "")
    product_id = request.args.get("product_id")
    category = request.args.get("category")
    try:
        limit = int(request.args.get("limit", 6))
    except ValueError:
        limit = 6
    return jsonify(
        {
            "query": query,
            "recommendations": engine.recommend(
                query=query,
                product_id=product_id,
                category=category,
                limit=limit,
            ),
        }
    )


@app.get("/api/products/<product_id>")
def product(product_id: str):
    item = engine.get_product(product_id)
    if not item:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(item)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
