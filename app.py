from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os

# Charger les variables d'environnement
load_dotenv()

# Initialiser Flask
app = Flask(__name__)
CORS(app)

# Initialiser OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt système pour cadrer l'IA
SYSTEM_PROMPT = {
    "role": "system",
    "content": """Tu es un professeur de trompette expérimenté. Voici comment tu dois répondre :

1. Si le problème décrit n'est pas encore clair ou précis, pose UNE seule question à la fois pour mieux comprendre. Ne propose PAS ENCORE d'exercice.
2. Quand tu es sûr du problème rencontré, propose UN SEUL exercice ciblé :
    - Sois clair, court, précis.
    - Utilise la notation latine (do, ré, mi…).
    - Indique quand le faire : échauffement, début, fin…
3. Seulement après avoir donné un exercice, termine toujours par cette phrase EXACTE :
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
        
        if not data or "messages" not in data:
            return jsonify({"error": "Requête invalide : pas de messages."}), 400
        
        user_messages = data["messages"]

        # Valider les messages correctement
        valid_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in user_messages
            if isinstance(msg, dict)
            and msg.get("role") in ["user", "assistant"]
            and isinstance(msg.get("content"), str)
            and msg.get("content").strip() != ""
        ]

        if not valid_messages:
            return jsonify({"error": "Aucun message utilisateur valide reçu."}), 400

        # Ajouter le système prompt
        conversation = [SYSTEM_PROMPT] + valid_messages

        # Appel OpenAI GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            temperature=0.4,
            max_tokens=800
        )

        ai_reply = response.choices[0].message.content.strip()

        return jsonify({"reply": ai_reply})

    except Exception as e:
        print(f"Erreur serveur: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Lancer le serveur Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
