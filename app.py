from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

# Créer un client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SYSTEM PROMPT : très clair, très strict
SYSTEM_PROMPT = {
    "role": "system",
    "content": """Tu es un professeur de trompette expérimenté.

Voici exactement comment tu dois répondre :

1. Quand l'utilisateur décrit un problème, commence par poser UNE seule question claire pour mieux comprendre.

2. Quand tu poses une question :
    - Si la réponse attendue est OUI ou NON, propose uniquement ces deux choix.
    - Sinon, propose entre 2 et 4 suggestions pertinentes et variées.

3. Quand tu proposes un exercice :
    - Décris UN SEUL exercice simple et efficace.
    - Termine toujours par : "Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"
    - NE propose AUCUNE suggestion dans ce cas.

IMPORTANT :
- Tu dois TOUJOURS répondre uniquement au format JSON brut, exactement comme ceci :
{
    "reply": "Le texte que tu veux afficher",
    "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
}
- Si aucune suggestion n'est nécessaire, renvoie une liste vide : "suggestions": []

NE JAMAIS sortir du format JSON, NE JAMAIS ajouter d'autres commentaires ou textes.
"""
}

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_messages = data.get("messages", [])

        # Validation : filtrer les messages valides
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

        # Ajouter le system prompt au début
        conversation = [SYSTEM_PROMPT] + valid_messages

        # Appel API OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            temperature=0.2  # plus précis
        )

        ai_message = response.choices[0].message.content.strip()

        # Essayer de parser directement la réponse
        parsed = json.loads(ai_message)

        return jsonify({
            "reply": parsed.get("reply", ""),
            "suggestions": parsed.get("suggestions", [])
        })

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
