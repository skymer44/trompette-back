from openai import OpenAI
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
Tu es un professeur de trompette expérimenté et bienveillant.

Important :
- Tu dois TOUJOURS répondre strictement en JSON.
- Le JSON doit contenir deux clés :
  - "reply" : le message principal affiché à l'utilisateur.
  - "suggestions" : un tableau (array) contenant 2 à 4 suggestions, ou [].

Nouvelles règles :
- Si ton "reply" est une vraie question (terminée par '?'), alors génère 2 à 4 suggestions d'options de réponse naturelles.
- Si ton "reply" n'est pas une question (pas de '?'), alors mets "suggestions": [].

Contraintes :
- N'écris jamais les suggestions dans le texte du "reply".
- Ton "reply" doit être naturel, humain et sans numérotation.

Exemples valides :
{"reply": "As-tu mal aux lèvres après avoir joué ?", "suggestions": ["Oui", "Non", "Parfois"]}
{"reply": "Voici un exercice pour t'aider à travailler ton souffle.", "suggestions": []}
"""
}

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_messages = data.get("messages", [])

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

        conversation = [SYSTEM_PROMPT] + valid_messages

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            temperature=0.7
        )

        raw_content = response.choices[0].message.content.strip()

        try:
            parsed_response = json.loads(raw_content)

            if "reply" in parsed_response and "suggestions" in parsed_response:
                return jsonify({
                    "reply": parsed_response["reply"],
                    "suggestions": parsed_response["suggestions"]
                })
            else:
                return jsonify({"error": "Réponse JSON invalide (clés manquantes)."}), 500

        except json.JSONDecodeError:
            print("Erreur de parsing JSON sur le contenu:", raw_content)
            return jsonify({"error": "Erreur de parsing JSON."}), 500

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
