from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify({"status": "ready", "model": "simple_flask"})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    # Simple echo response for testing
    response = f"Echo: {message}"

    return jsonify({"response": response, "status": "success"})


if __name__ == "__main__":
    print("🚀 Starting Simple Flask Server...")
    print("📍 Server running at: http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
