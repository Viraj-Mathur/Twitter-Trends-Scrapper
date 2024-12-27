from flask import Flask, render_template, jsonify
from pymongo import MongoClient
import os
from scrapper_module import scrape_x  # Import the main scraping function

# Initialize Flask app
app = Flask(__name__)

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # Default to local MongoDB if not provided
client = MongoClient(MONGO_URI)
db = client["twitter_trends"]
collection = db["trends"]

# Helper Function
def get_latest_record():
    """Fetch the latest record from MongoDB."""
    try:
        latest_record = collection.find().sort("timestamp", -1).limit(1)
        return latest_record.next()
    except StopIteration:
        return None


# Routes
@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")


@app.route("/run-script", methods=["GET"])
def run_script():
    """Run the scraper and save the results to MongoDB."""
    try:
        # Run the scraper
        print("[RUN-SCRIPT] Triggering the scraper...")
        scrape_x()

        # Fetch the latest record from MongoDB
        latest_record = get_latest_record()
        if not latest_record:
            return jsonify({"status": "error", "message": "No data was fetched by the scraper."})

        return jsonify({"status": "success", "data": latest_record})

    except Exception as e:
        print(f"[RUN-SCRIPT] Error: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route("/get-latest-data", methods=["GET"])
def get_latest_data():
    """Fetch the latest trending data from MongoDB."""
    try:
        # Fetch the latest record from MongoDB
        latest_record = get_latest_record()
        if not latest_record:
            return jsonify({"status": "error", "message": "No data available in MongoDB."})

        return jsonify({"status": "success", "data": latest_record})

    except Exception as e:
        print(f"[GET-LATEST-DATA] Error: {e}")
        return jsonify({"status": "error", "message": str(e)})


# Main Entry Point
if __name__ == "__main__":
    app.run(debug=True)
