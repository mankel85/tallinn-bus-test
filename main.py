from flask import Flask, jsonify, render_template, request
from gtfs_tools import get_schedule_for_route

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.before_request
def before_any():
    print("Request received:", request.path)

@app.route("/")
def home():
    print("Serving home route")
    return render_template("index.html", routes=[])  # routes handled via JS

@app.route("/api/routes")
def get_routes():
    from gtfs_tools import find_oilme_stops_and_routes
    try:
        data = find_oilme_stops_and_routes()
        return jsonify(data["routes_with_oilme"])
    except Exception as e:
        print("Error loading routes:", e)
        return jsonify([])

@app.route("/api/schedule/<route>")
def schedule(route):
    try:
        return jsonify(get_schedule_for_route(route))
    except Exception as e:
        print("Error in schedule API:", e)
        return jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
