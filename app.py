
import os
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__)

# Ollama Cloud offers an OpenAI-compatible API.
api_key = os.environ.get("OLLAMA_API_KEY")

client = OpenAI(
    base_url="https://ollama.com/v1",
    api_key=api_key or "missing-key"
)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not api_key:
        return jsonify({
            "reply": "My AI connection isn't configured yet."
        }), 503

    data = request.get_json(silent=True) or {}
    question = data.get("message", "").strip()

    if not question:
        return jsonify({"reply": "Please ask me something."}), 400

    try:
        response = client.chat.completions.create(
            model=os.environ.get("OLLAMA_MODEL", "gpt-oss:20b-cloud"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, a helpful personal AI assistant. "
                        "Answer clearly and naturally. Keep replies concise "
                        "because they will be spoken aloud."
                    )
                },
                {"role": "user", "content": question}
            ]
        )

        answer = response.choices[0].message.content
        return jsonify({"reply": answer or "I couldn't create a reply."})

    except Exception:
        app.logger.exception("AI request failed")
        return jsonify({
            "reply": "I couldn't reach my AI service. Please try again."
        }), 502
