"""Flask server and SQLite storage for the Atiçadores LTDA website."""
from __future__ import annotations

import os
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

SITE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = SITE_DIR / "frontend"
SCHEMA_PATH = Path(__file__).resolve().parent / "database" / "schema.sql"
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "database" / "suggestions.sqlite3"
DB_PATH = Path(os.environ.get("ATICADORES_DB_PATH", str(DEFAULT_DB_PATH))).expanduser()
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


def initialize_database() -> None:
    """Create the suggestions table if this is the first server launch."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH, timeout=10)) as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


initialize_database()


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/suggestions")
def create_suggestion():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Envie os dados do formulário em formato JSON."}), 400

    name = payload.get("name", "")
    email = payload.get("email", "")
    suggestion = payload.get("suggestion", "")
    if not all(isinstance(value, str) for value in (name, email, suggestion)):
        return jsonify({"error": "Confira os campos e tente novamente."}), 400

    name, email, suggestion = name.strip(), email.strip(), suggestion.strip()
    if not 2 <= len(name) <= 80:
        return jsonify({"error": "O nome precisa ter entre 2 e 80 caracteres."}), 400
    if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        return jsonify({"error": "Digite um endereço de e-mail válido."}), 400
    if not 10 <= len(suggestion) <= 2000:
        return jsonify({"error": "A sugestão precisa ter entre 10 e 2.000 caracteres."}), 400

    try:
        with closing(sqlite3.connect(DB_PATH, timeout=10)) as connection:
            connection.execute(
                "INSERT INTO suggestions (name, email, suggestion) VALUES (?, ?, ?)",
                (name, email, suggestion),
            )
            connection.commit()
    except sqlite3.Error:
        app.logger.exception("Could not save a game suggestion")
        return jsonify({"error": "Ocorreu um erro ao salvar. Tente novamente mais tarde."}), 500

    return jsonify({"message": "Sugestão salva com sucesso."}), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
