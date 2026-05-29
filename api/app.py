# api/app.py

import json
import os
from flask import Flask, jsonify, abort, request

app = Flask(__name__)

DATA_DIR      = "/data/cache"
HOME_CACHE    = f"{DATA_DIR}/home.json"
DEVICE_CONFIG = f"{DATA_DIR}/device_config.json"

@app.route("/api/full-sync")
def full_sync():
    """Main endpoint — Kindle polls this to get everything"""
    if not os.path.exists(HOME_CACHE):
        abort(503, description="Cache not ready yet")

    with open(HOME_CACHE) as f:
        home = json.load(f)

    # if device sends coordinates, save for fetcher to use on next run
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if lat and lon:
        try:
            with open(DEVICE_CONFIG, "w") as f:
                json.dump({"lat": float(lat), "lon": float(lon)}, f)
        except Exception as e:
            print(f"  failed to save device config: {e}")

    # load per-source headlines
    sources = {}
    sources_dir = f"{DATA_DIR}/sources"
    if os.path.exists(sources_dir):
        for fname in os.listdir(sources_dir):
            if fname.endswith(".json"):
                source_id = fname[:-5]
                with open(f"{sources_dir}/{fname}") as f:
                    sources[source_id] = json.load(f)

    # collect url_hashes referenced by current source headlines
    referenced = set()
    for items in sources.values():
        for item in items:
            if "url_hash" in item:
                referenced.add(item["url_hash"])

    # only serve articles that are currently referenced
    articles = {}
    articles_dir = f"{DATA_DIR}/articles"
    if os.path.exists(articles_dir):
        for fname in os.listdir(articles_dir):
            if fname.endswith(".txt"):
                url_hash = fname[:-4]
                if url_hash in referenced:
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