from flask import Flask, request, jsonify
import subprocess
import threading
import time

app = Flask(__name__)

# Function to run scripts in separate threads with error handling
def run_script(script_name):
    def target():
        try:
            subprocess.run(["python", script_name], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running {script_name}: {e}")

    threading.Thread(target=target, daemon=True).start()

# API Endpoints
@app.route("/start_voice", methods=["POST"])
def start_voice():
    run_script("Main.py")
    return jsonify({"message": "Voice automation started"})

@app.route("/start_hand", methods=["POST"])
def start_hand():
    run_script("gestcon.py")
    return jsonify({"message": "Hand gesture control started"})

@app.route("/start_game", methods=["POST"])
def start_game():
    run_script("app.py")
    return jsonify({"message": "Game gesture control started"})

@app.route("/start_eye", methods=["POST"])
def start_eye():
    run_script("eye.py")
    return jsonify({"message": "Eye tracking started"})

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"message": "Server is running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
