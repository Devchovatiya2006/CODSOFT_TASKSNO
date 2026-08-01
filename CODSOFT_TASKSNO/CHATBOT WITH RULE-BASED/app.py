from flask import Flask, render_template, request, jsonify
from chatbot import RuleBasedChatbot

app = Flask(__name__)
bot = RuleBasedChatbot()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "No message provided"}), 400
    result = bot.respond(message)
    return jsonify(result)


@app.route("/api/reset", methods=["POST"])
def reset():
    bot.reset()
    return jsonify({"status": "ok", "message": "Memory cleared."})


if __name__ == "__main__":
    print("🚀  RuleBot running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
