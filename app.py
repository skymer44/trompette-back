from openai import OpenAI
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

# Créer l'application Flask
app = Flask(__name__)
CORS(app)

# Créer un client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt système structuré
SYSTEM_PROMPT = {
    "role": "system",
    "content": """Tu es un professeur de trompette expérimenté. Voici comment tu dois répondre :

1. Si le problème décrit n'est pas encore clair ou précis, pose UNE seule question à la fois pour mieux comprendre. Ne propose PAS ENCORE d'exercice.
2. Quand tu es sûr du problème rencontré, propose UN SEUL exercice ciblé.
    - Sois clair, court, précis.
    - Utilise la notation latine (do, ré, mi…).
    - Indique quand le faire : échauffement, début, fin…
3. Seulement après avoir donné un exercice, termine par cette phrase EXACTE :
"Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"

Important :

- Ne donne JAMAIS une question ET un exercice dans le même message.
- Ne demande de feedback que si un exercice a été donné.
- Sois pédagogue, humain et bienveillant.
"""
}

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_messages = data.get("messages", [])

        # Validation
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

        # Appel à OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation
        )

        return jsonify({"reply": response.choices[0].message.content})

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
