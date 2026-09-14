from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from ai_engine import ask_darkia


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/style.css")
def style():
    return send_from_directory(BASE_DIR, "style.css")


@app.route("/script.js")
def script():
    return send_from_directory(BASE_DIR, "script.js")


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "name": "DARKIA",
        "version": "2.0",
        "status": "online"
    })


@app.route("/api/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json(silent=True) or {}

        message = data.get("message", "").strip()
        history = data.get("history", [])

        if not message:
            return jsonify({
                "response": "Escreve uma mensagem primeiro."
            }), 400

        response = ask_darkia(
            message,
            history
        )

        return jsonify({
            "response": response,
            "speak": False
        })

    except Exception as error:

        return jsonify({
            "response": f"Erro interno da DARKIA: {error}"
        }), 500


if __name__ == "__main__":

    print()
    print("================================")
    print("          DARKIA V2")
    print("================================")
    print("Servidor: ONLINE")
    print("Endereço: http://127.0.0.1:5000")
    print("================================")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
