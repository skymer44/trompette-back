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

# Créer un client OpenAI avec la clé API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt système structuré
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
Tu es un professeur de trompette expérimenté et bienveillant.

Important :
- Tu dois TOUJOURS répondre strictement en JSON.
- Le JSON doit contenir deux clés : 
  - "reply" : la phrase principale que tu veux afficher à l'utilisateur (sans liste, sans numérotation)
  - "suggestions" : un tableau (array) de 2 à 4 suggestions possibles à cliquer.

Règles :
- Si tu poses une question (par exemple pour clarifier un problème), génère entre 2 et 4 suggestions courtes et naturelles.
- Si tu proposes un exercice, alors :
  - Le "reply" contient l'explication de l'exercice.
  - Le "suggestions" doit être vide [].

Attention :
- Tu ne dois jamais écrire les suggestions dans le texte principal ("reply").
- Le "reply" doit être naturel et sans numérotation.
- Le JSON doit être valide.

Exemples corrects :
{"reply": "Est-ce que tu ressens une tension dans l'embouchure ?", "suggestions": ["Oui", "Non", "Parfois"]}
{"reply": "Voici un exercice pour améliorer ton souffle...", "suggestions": []}
"""
}

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_messages = data.get("messages", [])

        # Validation basique
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

        # Conversation complète
        conversation = [SYSTEM_PROMPT] + valid_messages

        # Appel à OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            temperature=0.7
        )

        raw_content = response.choices[0].message.content.strip()

        # Essayer de parser proprement le JSON
        try:
            parsed_response = json.loads(raw_content)

            # Vérifier que les bonnes clés existent
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
