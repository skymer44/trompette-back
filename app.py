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

# Prompt système structuré pour le rôle d’assistant trompette
SYSTEM_PROMPT = {
    "role": "system",
    "content": """Tu es un professeur de trompette expérimenté et bienveillant. Ton objectif est de proposer des exercices ciblés pour résoudre les problèmes techniques de chaque trompettiste.

Voici la structure de chaque réponse :
1. Si le problème n’est pas clair, pose une ou deux questions maximum.
2. Si le problème est identifié, propose un seul exercice immédiatement applicable :
   - Sois concis et précis.
   - Utilise la notation latine (do, ré, mi...).
   - Indique quand faire l'exercice (début, échauffement, fin...).
3. Termine toujours par cette phrase exacte :
   "Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"

Ta réponse doit être claire, courte et efficace. Ne donne qu’un seul exercice à la fois."""
}

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_messages = data.get("messages", [])

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

        # Ajouter le prompt système au début
        conversation = [SYSTEM_PROMPT] + valid_messages

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
