import json
import uuid
import base64
from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

DOKU_MCP_URL = config["doku"]["mcp_url"]
DOKU_CLIENT_ID = config["doku"]["client_id"]
DOKU_API_KEY = config["doku"]["api_key"]

def build_headers():
    encoded = base64.b64encode(f"{DOKU_API_KEY}:".encode()).decode()
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Client-Id": DOKU_CLIENT_ID,
        "Authorization": f"Basic {encoded}"
    }

def call_mcp(method, params=None):
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params or {}
    }

    print("==== MCP REQUEST ====")
    print(json.dumps(payload, indent=2))
    print("=====================")

    resp = requests.post(
        DOKU_MCP_URL,
        headers=build_headers(),
        data=json.dumps(payload),
        timeout=60
    )

    print("==== MCP RESPONSE ====")
    print(resp.text)
    print("======================")

    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return resp.json()

    return {"raw": resp.text}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/test-connection")
def test_connection():
    try:
        result = call_mcp("tools/list", {})
        return jsonify({"ok": True, "data": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/tools")
def tools():
    try:
        result = call_mcp("tools/list", {})
        return jsonify({"ok": True, "data": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/call", methods=["POST"])
def call_tool():
    try:
        body = request.get_json(force=True)
        name = body.get("name", "").strip()
        arguments = body.get("arguments", {})

        if not name:
            return jsonify({"ok": False, "error": "Tool name is required"}), 400

        if "toolRequest" not in arguments:
            arguments = {"toolRequest": arguments}

        result = call_mcp("tools/call", {
            "name": name,
            "arguments": arguments
        })
        return jsonify({"ok": True, "data": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(
        host=config["app"]["host"],
        port=config["app"]["port"],
        debug=config["app"]["debug"]
    )
