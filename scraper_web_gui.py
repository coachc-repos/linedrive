#!/usr/bin/env python3
"""
LineDrive Scraper Web GUI

Web interface for running Perfect Game tournament scrapers with configurable parameters.
"""

import os
import sys
import json
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Add project root to path
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))

from batch_scrapers.perfect_game.perfect_game_scraper import PerfectGameScraper
from batch_scrapers.perfect_game.filters import PerfectGameFilters

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates/scraper")

# Store for active scrape jobs
scrape_jobs = {}


@app.route("/")
def index():
    """Serve the scraper GUI"""
    return render_template(
        "scraper_index.html",
        age_groups=PerfectGameFilters.AGE_GROUPS,
        sport_types=PerfectGameFilters.SPORT_TYPES,
        states=PerfectGameFilters.STATES,
        city_coords=PerfectGameFilters.CITY_COORDS,
    )


@app.route("/api/scrape", methods=["POST"])
def start_scrape():
    """Start a Perfect Game scrape with the given filters"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No parameters provided"}), 400

    state = data.get("state", "TX")
    city = data.get("city", "Houston")
    radius = int(data.get("radius", 25))
    age_group = data.get("age_group", "10U")
    sport_type = data.get("sport_type", "Baseball")
    start_date = data.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    end_date = data.get("end_date", (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d"))

    # Look up city coordinates
    city_key = city.lower().strip()
    coords = PerfectGameFilters.CITY_COORDS.get(city_key, {"lat": 29.786, "lng": -95.3885})

    filters = {
        "state": state,
        "city": city,
        "lat": coords["lat"],
        "lng": coords["lng"],
        "radius": radius,
        "sport_type": sport_type,
        "age_group": age_group,
        "start_date": start_date,
        "end_date": end_date,
    }

    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    scrape_jobs[job_id] = {"status": "running", "filters": filters, "results": None}

    def run_scrape():
        try:
            scraper = PerfectGameScraper(headless=True, debug=True)
            results = scraper.search_tournaments(filters)
            scrape_jobs[job_id]["results"] = results
            scrape_jobs[job_id]["status"] = "completed"

            # Save results to file
            os.makedirs("output", exist_ok=True)
            filepath = f"output/perfect_game_results_{job_id}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            scrape_jobs[job_id]["filepath"] = filepath
            logger.info(f"Scrape {job_id} completed: {len(results.get('tournaments', []))} tournaments")
        except Exception as e:
            logger.error(f"Scrape {job_id} failed: {e}")
            scrape_jobs[job_id]["status"] = "error"
            scrape_jobs[job_id]["error"] = str(e)

    thread = threading.Thread(target=run_scrape, daemon=True)
    thread.start()

    return jsonify({"job_id": job_id, "status": "running", "filters": filters})


@app.route("/api/scrape/<job_id>", methods=["GET"])
def get_scrape_status(job_id):
    """Check the status of a scrape job"""
    job = scrape_jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/api/results", methods=["GET"])
def list_results():
    """List all saved result files"""
    output_dir = REPO_ROOT / "output"
    if not output_dir.exists():
        return jsonify({"files": []})

    files = sorted(
        [f.name for f in output_dir.glob("perfect_game_results_*.json")],
        reverse=True,
    )
    return jsonify({"files": files})


@app.route("/api/results/<filename>", methods=["GET"])
def get_result_file(filename):
    """Get contents of a specific result file"""
    # Sanitize filename to prevent path traversal
    safe_name = Path(filename).name
    if not safe_name.startswith("perfect_game_results_") or not safe_name.endswith(".json"):
        return jsonify({"error": "Invalid filename"}), 400

    filepath = REPO_ROOT / "output" / safe_name
    if not filepath.exists():
        return jsonify({"error": "File not found"}), 404

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


if __name__ == "__main__":
    print("🏆 LineDrive Scraper Web GUI")
    print(f"📍 http://localhost:8081")
    print(f"📂 Results saved to: {REPO_ROOT / 'output'}")
    app.run(host="0.0.0.0", port=8081, debug=False)
