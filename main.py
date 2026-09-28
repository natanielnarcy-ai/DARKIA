from pathlib import Path
import sqlite3
from functools import wraps

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    session,
)

from ai_engine import ask_darkia
from whatsapp_commands import process_command

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "darkia.db"

app = Flask(__name__)
app.secret_key = "DARKIA-CHANGE-THIS-SECRET-KEY"


# =========================================================
# BANCO DE DADOS
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# AUTENTICAÇÃO
# =========================================================

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({
                "status": "error",
                "response": "É necessário iniciar sessão."
            }), 401

        return function(*args, **kwargs)

    return wrapper


# =========================================================
# PÁGINAS
# =========================================================

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/style.css")
def style():
    return send_from_directory(BASE_DIR, "style.css")


@app.route("/script.js")
def script():
    return send_from_directory(BASE_DIR, "script.js")


@app.route("/darkia-voice-avatar.png")
def darkia_voice_avatar():
    return send_from_directory(BASE_DIR, "darkia-voice-avatar.png")


# =========================================================
# CONTA — CRIAR
# =========================================================

@app.route("/api/register", methods=["POST"])
def register():
    try:
        from werkzeug.security import generate_password_hash

        data = request.get_json(silent=True) or {}

        username = data.get("username", "").strip()
        password = data.get("password", "")

        if len(username) < 3:
            return jsonify({
                "status": "error",
                "response": "O nome de utilizador deve ter pelo menos 3 caracteres."
            }), 400

        if len(password) < 6:
            return jsonify({
                "status": "error",
                "response": "A palavra-passe deve ter pelo menos 6 caracteres."
            }), 400

        password_hash = generate_password_hash(password)

        conn = get_db()

        try:
            cursor = conn.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
                """,
                (username, password_hash)
            )

            user_id = cursor.lastrowid
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()

            return jsonify({
                "status": "error",
                "response": "Esse nome de utilizador já existe."
            }), 409

        conn.close()

        session["user_id"] = user_id
        session["username"] = username

        return jsonify({
            "status": "ok",
            "response": "Conta criada com sucesso.",
            "user": {
                "id": user_id,
                "username": username
            }
        })

    except Exception as error:
        return jsonify({
            "status": "error",
            "response": f"Erro ao criar conta: {error}"
        }), 500


# =========================================================
# CONTA — LOGIN
# =========================================================

@app.route("/api/login", methods=["POST"])
def login():
    try:
        from werkzeug.security import check_password_hash

        data = request.get_json(silent=True) or {}

        username = data.get("username", "").strip()
        password = data.get("password", "")

        conn = get_db()

        user = conn.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        conn.close()

        if not user or not check_password_hash(
            user["password_hash"],
            password
        ):
            return jsonify({
                "status": "error",
                "response": "Nome de utilizador ou palavra-passe incorretos."
            }), 401

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return jsonify({
            "status": "ok",
            "response": "Sessão iniciada.",
            "user": {
                "id": user["id"],
                "username": user["username"]
            }
        })

    except Exception as error:
        return jsonify({
            "status": "error",
            "response": f"Erro no login: {error}"
        }), 500


# =========================================================
# CONTA — SESSÃO ATUAL
# =========================================================

@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({
            "logged_in": False
        })

    return jsonify({
        "logged_in": True,
        "user": {
            "id": session["user_id"],
            "username": session["username"]
        }
    })


# =========================================================
# LOGOUT
# =========================================================

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "status": "ok",
        "response": "Sessão terminada."
    })


# =========================================================
# NOVA CONVERSA
# =========================================================

@app.route("/api/conversations", methods=["POST"])
@login_required
def create_conversation():
    try:
        data = request.get_json(silent=True) or {}

        title = data.get(
            "title",
            "Nova conversa"
        ).strip()

        if not title:
            title = "Nova conversa"

        conn = get_db()

        cursor = conn.execute(
            """
            INSERT INTO conversations (user_id, title)
            VALUES (?, ?)
            """,
            (session["user_id"], title)
        )

        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            "status": "ok",
            "conversation": {
                "id": conversation_id,
                "title": title
            }
        })

    except Exception as error:
        return jsonify({
            "status": "error",
            "response": f"Erro ao criar conversa: {error}"
        }), 500


# =========================================================
# HISTÓRICO
# =========================================================

@app.route("/api/conversations", methods=["GET"])
@login_required
def conversations():
    conn = get_db()

    rows = conn.execute(
        """
        SELECT id, title, created_at, updated_at
        FROM conversations
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return jsonify({
        "status": "ok",
        "conversations": [dict(row) for row in rows]
    })


# =========================================================
# MENSAGENS DE UMA CONVERSA
# =========================================================

@app.route("/api/conversations/<int:conversation_id>", methods=["GET"])
@login_required
def conversation(conversation_id):
    conn = get_db()

    conv = conn.execute(
        """
        SELECT id, title, created_at, updated_at
        FROM conversations
        WHERE id = ? AND user_id = ?
        """,
        (conversation_id, session["user_id"])
    ).fetchone()

    if not conv:
        conn.close()

        return jsonify({
            "status": "error",
            "response": "Conversa não encontrada."
        }), 404

    messages = conn.execute(
        """
        SELECT role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
        """,
        (conversation_id,)
    ).fetchall()

    conn.close()

    return jsonify({
        "status": "ok",
        "conversation": dict(conv),
        "messages": [dict(message) for message in messages]
    })


# =========================================================
# CHAT
# =========================================================

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}

        message = data.get("message", "").strip()
        history = data.get("history", [])
        conversation_id = data.get("conversation_id")

        if not message:
            return jsonify({
                "response": "Escreve uma mensagem primeiro."
            }), 400

        response = ask_darkia(
            message,
            history
        )

        # Guardar histórico apenas se existir sessão
        if "user_id" in session:

            conn = get_db()

            # Se não existe conversa, criar uma automaticamente
            if not conversation_id:

                title = message[:50]

                cursor = conn.execute(
                    """
                    INSERT INTO conversations (user_id, title)
                    VALUES (?, ?)
                    """,
                    (session["user_id"], title)
                )

                conversation_id = cursor.lastrowid

            # Confirmar que a conversa pertence ao utilizador
            conversation = conn.execute(
                """
                SELECT id
                FROM conversations
                WHERE id = ? AND user_id = ?
                """,
                (conversation_id, session["user_id"])
            ).fetchone()

            if conversation:

                conn.execute(
                    """
                    INSERT INTO messages
                    (conversation_id, role, content)
                    VALUES (?, ?, ?)
                    """,
                    (
                        conversation_id,
                        "user",
                        message
                    )
                )

                conn.execute(
                    """
                    INSERT INTO messages
                    (conversation_id, role, content)
                    VALUES (?, ?, ?)
                    """,
                    (
                        conversation_id,
                        "assistant",
                        response
                    )
                )

                conn.execute(
                    """
                    UPDATE conversations
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (conversation_id,)
                )

                conn.commit()

            conn.close()

        return jsonify({
            "response": response,
            "speak": False,
            "conversation_id": conversation_id
        })

    except Exception as error:
        return jsonify({
            "response": f"Erro interno da DARKIA: {error}"
        }), 500


# =========================================================
# WHATSAPP
# =========================================================

@app.route("/api/whatsapp", methods=["POST"])
def whatsapp():
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()

        if not message:
            return jsonify({
                "response": "DARKIA: Mensagem vazia."
            }), 400

        response = process_command(message)

        if response is None:
            response = (
                "DARKIA: 🤖 Comando não reconhecido.\n"
                "Usa !menu para ver os comandos."
            )

        return jsonify({
            "response": response,
            "status": "ok"
        })

    except Exception as error:
        return jsonify({
            "response": f"DARKIA: Erro interno: {error}",
            "status": "error"
        }), 500


# =========================================================
# STATUS
# =========================================================

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "name": "DARKIA",
        "version": "2.0",
        "status": "online"
    })


# =========================================================
# INICIALIZAÇÃO
# =========================================================

init_db()


if __name__ == "__main__":

    print()
    print("================================")
    print("          DARKIA V2")
    print("================================")
    print("Servidor: ONLINE")
    print("Endereço: http://127.0.0.1:5000")
    print("Banco: darkia.db")
    print("Contas: ATIVADAS")
    print("Histórico: ATIVADO")
    print("================================")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
