
from flask import Flask, render_template, jsonify, request
import sqlite3
import json
import urllib.request
import random
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "quotes.db"
SEED_PATH = BASE_DIR / "quote_fallback_data.json"


# Connect to database
def connect_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


# Create favorites table
def create_database():
    con = connect_db()

    con.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL,
            author TEXT NOT NULL,
            UNIQUE(quote, author)
        )
    """)

    con.commit()
    con.close()


# Get random quote from public API
def get_random_quote():
    try:
        url = "https://dummyjson.com/quotes/random"

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "QuoteGenerator/1.0"}
        )

        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))

        return {
            "quote": data["quote"],
            "author": data["author"],
            "source": "API"
        }

    except Exception:
        # Use local quotes if API fails
        with open(SEED_PATH, "r", encoding="utf-8") as file:
            quotes = json.load(file)

        quote = random.choice(quotes)

        return {
            "quote": quote["quote"],
            "author": quote["author"],
            "source": "Fallback"
        }


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Get a random quote
@app.route("/api/quote")
def random_quote():
    return jsonify(get_random_quote())


# Save favorite quote
@app.route("/api/favorites", methods=["POST"])
def add_favorite():
    data = request.get_json()

    if not data or not data.get("quote") or not data.get("author"):
        return jsonify({"error": "Quote and author are required"}), 400

    con = connect_db()

    try:
        con.execute(
            "INSERT INTO favorites (quote, author) VALUES (?, ?)",
            (data["quote"], data["author"])
        )
        con.commit()

        return jsonify({"message": "Favorite saved successfully"})

    except sqlite3.IntegrityError:
        return jsonify({"message": "Quote already saved"}), 409

    finally:
        con.close()


# Get favorite history
@app.route("/api/favorites")
def get_favorites():
    con = connect_db()

    favorites = con.execute(
        "SELECT * FROM favorites ORDER BY id DESC"
    ).fetchall()

    con.close()

    return jsonify([dict(item) for item in favorites])


# Delete favorite quote
@app.route("/api/favorites/<int:id>", methods=["DELETE"])
def delete_favorite(id):
    con = connect_db()

    cur = con.execute(
        "DELETE FROM favorites WHERE id = ?", (id,)
    )

    con.commit()
    con.close()

    if cur.rowcount == 0:
        return jsonify({"error": "Favorite not found"}), 404

    return jsonify({"message": "Favorite deleted"})


if __name__ == "__main__":
    create_database()

    app.run(
        host="0.0.0.0",
        port=int(__import__("os").environ.get("PORT", 5000)),
        debug=False
    )
