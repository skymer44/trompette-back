from openai import OpenAI
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement (dont OPENAI_API_KEY)
load_dotenv()

app = Flask(__name__)
CORS(app)

# Créer un client OpenAI avec la clé API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt système général (sans structure imposée pour "guided")
SYSTEM_PROMPT = {
    "role": "system",
    "content": "Tu es un professeur de trompette expérimenté, bienveillant et à l'écoute. Tu donnes des réponses utiles et pédagogiques, avec des conseils concrets. Tu peux aussi poser des questions pour clarifier les besoins de l'utilisateur."
}

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_messages = data.get("messages", [])
        mode = data.get("mode", "free")

        # Validation : messages doit être une liste de dicts avec un champ "content" texte
        valid_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in user_messages
            if isinstance(msg, dict)
            and "role" in msg
            and "content" in msg
            and isinstance(msg["content"], str)
            and msg["content"].strip() != ""
        ]

        if not valid_messages:
            return jsonify({"error": "Aucun message utilisateur valide reçu."}), 400

        # Ajouter le prompt système si on est en mode guided
        if mode == "guided":
            conversation = [SYSTEM_PROMPT] + valid_messages
        else:
            conversation = valid_messages

        # Appel à l'API OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )

        return jsonify({"reply": response.choices[0].message.content})

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
