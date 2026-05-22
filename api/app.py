# api/app.py

import json
import os
from flask import Flask, jsonify, abort

app = Flask(__name__)

DATA_DIR    = "/data/cache"
HOME_CACHE  = f"{DATA_DIR}/home.json"

@app.route("/api/full-sync")
def full_sync():
    """Main endpoint — Kindle polls this to get everything"""
    if not os.path.exists(HOME_CACHE):
        abort(503, description="Cache not ready yet")

    with open(HOME_CACHE) as f:
        home = json.load(f)

    # load per-source headlines
    sources = {}
    sources_dir = f"{DATA_DIR}/sources"
    if os.path.exists(sources_dir):
        for fname in os.listdir(sources_dir):
            if fname.endswith(".json"):
                source_id = fname[:-5]
                with open(f"{sources_dir}/{fname}") as f:
                    sources[source_id] = json.load(f)

    # load pre-cached articles
    articles = {}
    articles_dir = f"{DATA_DIR}/articles"
    if os.path.exists(articles_dir):
        for fname in os.listdir(articles_dir):
            if fname.endswith(".txt"):
                url_hash = fname[:-4]
                with open(f"{articles_dir}/{fname}") as f:
                    articles[url_hash] = f.read()

    return jsonify({
        "home":     home,
        "sources":  sources,
        "articles": articles,
    })

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)