from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

# Charger les variables d'environnement (comme OPENAI_API_KEY)
load_dotenv()

app = Flask(__name__)
CORS(app)

# Créer un client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SYSTEM PROMPT corrigé
SYSTEM_PROMPT = {
    "role": "system",
    "content": """Tu es un professeur de trompette expérimenté.

Voici comment tu dois répondre :

1. Quand l'utilisateur décrit un problème, commence par poser UNE seule question courte et simple pour mieux comprendre.

2. Quand tu poses une question :
    - Si la réponse logique est OUI ou NON, propose uniquement ces deux choix.
    - Sinon, propose entre 3 et 4 suggestions variées adaptées.

Formate les suggestions ainsi, sans rien écrire autour :

Suggestions: 
- Réponse 1
- Réponse 2
- Réponse 3

3. Quand le problème est suffisamment clair, propose UN SEUL exercice ciblé. Termine alors ton message par cette phrase EXACTE :
"Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"

Important :
- Ne propose jamais de suggestions après un exercice.
- Sois simple, clair, pédagogue et bienveillant.
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

        # Ajouter le système prompt au début
        conversation = [SYSTEM_PROMPT] + valid_messages

        # Appel API OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation
        )

        ai_message = response.choices[0].message.content.strip()

        # Extraire suggestions si présentes
        suggestions = []
        if "Suggestions:" in ai_message:
            parts = ai_message.split("Suggestions:")
            ai_message = parts[0].strip()
            suggestion_lines = parts[1].strip().splitlines()
            suggestions = [line.lstrip("- ").strip() for line in suggestion_lines if line.strip()]

        return jsonify({
            "reply": ai_message,
            "suggestions": suggestions
        })

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
