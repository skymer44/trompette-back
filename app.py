from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os

# Charger les variables d'environnement (.env)
load_dotenv()

# Initialiser Flask
app = Flask(__name__)
CORS(app)

# Initialiser OpenAI avec la clé d'API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt système de l'IA
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
        
        # Validation des messages
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

        # Construire la conversation avec le prompt système
        conversation = [SYSTEM_PROMPT] + valid_messages

        # Choix du modèle (GPT-4o pour rapidité et qualité)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            temperature=0.5,  # Un peu de créativité mais reste très rigoureux
            max_tokens=800  # Limite pour éviter des réponses trop longues
        )

        ai_reply = response.choices[0].message.content.strip()

        return jsonify({"reply": ai_reply})

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

# Lancer l'application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
