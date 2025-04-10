from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)  # autorise les requêtes depuis ton front React

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({ "reply": "Tu n'as rien écrit. Essaie à nouveau !" }), 400

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                { "role": "system", "content": "Tu es un professeur de trompette expérimenté et bienveillant. Ton objectif est d’aider chaque trompettiste à résoudre ses problèmes techniques en trouvant pour lui l’exercice le plus efficace possible. Réponds toujours en français." },
                { "role": "user", "content": user_message }
            ]
        )

        bot_reply = response.choices[0].message.content.strip()
        return jsonify({ "reply": bot_reply })

    except Exception as e:
        print("Erreur côté serveur :", e)
        return jsonify({ "reply": "Une erreur est survenue côté serveur. Réessaie plus tard." }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
