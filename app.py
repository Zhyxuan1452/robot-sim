"""HTTP 层：只做请求转发与静态页面托管，不做移动判断。"""
from flask import Flask, jsonify, request, send_from_directory
from sim import Sim

app = Flask(__name__, static_folder="static", static_url_path="")
sim = Sim(
    width=10,
    height=10,
    start=(1, 1),
    obstacles=[(2, 1), (4, 4), (4, 5), (6, 7), (7, 7), (8, 2)],
)


@app.get("/api/state")
def api_state():
    return jsonify(sim.to_dict())


@app.post("/api/move")
def api_move():
    data = request.get_json(silent=True) or {}
    return jsonify(sim.move(data.get("dir")))


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)