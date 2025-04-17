from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os

# Charger les variables d'environnement (dont OPENAI_API_KEY)
load_dotenv()

app = Flask(__name__)
CORS(app)

# Client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt système
SYSTEM_PROMPT = {
    "role": "system",
    "content": """Tu es un professeur de trompette expérimenté. Voici les règles strictes à suivre pour répondre :

1. Si tu poses une question pour mieux comprendre, propose aussi entre 2 à 4 suggestions typiques dans un tableau JSON nommé 'suggestions'. Ne mets PAS ces suggestions dans ton texte principal.
2. Si tu proposes un exercice, n'ajoute aucune suggestion (le tableau suggestions doit être vide).
3. Ne donne JAMAIS une question et un exercice dans le même message.
4. Sois toujours clair, pédagogue et bienveillant.

À CHAQUE réponse, respecte ce format exact :

{
  "reply": "Texte principal de la réponse (question ou exercice)",
  "suggestions": ["Réponse 1", "Réponse 2", "Réponse 3"]
}

Si tu proposes un exercice, alors renvoie :
{
  "reply": "Texte principal de l'exercice",
  "suggestions": []
}

ATTENTION : Tu dois toujours répondre en JSON valide, sans jamais sortir de ce format."""
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

        # Ajouter le prompt système
        conversation = [SYSTEM_PROMPT] + valid_messages

        # Appel OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            response_format="json"  # Demander explicitement du JSON
        )

        # Récupérer directement le JSON retourné
        raw_reply = response.choices[0].message.content

        # Convertir en dict
        import json
        parsed_reply = json.loads(raw_reply)

        # Sécuriser la réponse retournée au front
        return jsonify({
            "reply": parsed_reply.get("reply", "Réponse vide."),
            "suggestions": parsed_reply.get("suggestions", [])
        })

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
