import subprocess
from flask import Flask, jsonify, render_template
from pymongo import MongoClient


app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"  # Replace with your MongoDB URI
DB_NAME = "twitter_trends"
COLLECTION_NAME = "trending_topics"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-and-get-data', methods=['GET'])
def fetch_and_get_data():
    try:
        # Step 1: Run the Selenium script using subprocess
        result = subprocess.run(["python", "test.py"], capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({"error": "Failed to run the Selenium script", "message": result.stderr}), 500

        # Step 2: Retrieve the latest stored data from MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Retrieve the latest data
        latest_data = collection.find_one(sort=[("_id", -1)])  # Sort by `_id` descending
        if latest_data:
            latest_data["_id"] = str(latest_data["_id"])  # Convert ObjectId to string for JSON serialization
            return jsonify(latest_data)
        else:
            return jsonify({"error": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
