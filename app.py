from openai import OpenAI
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

# Créer un client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt système structuré
SYSTEM_PROMPT = {
    "role": "system",
    "content": """Tu es un professeur de trompette expérimenté.

Voici comment tu dois répondre :

1. Quand l'utilisateur explique un problème, commence par poser UNE seule question courte et simple pour mieux comprendre.

2. Quand tu poses une question, propose aussi 3 ou 4 suggestions de réponses adaptées que l'utilisateur pourra sélectionner.

Formate les suggestions ainsi dans ta réponse (sans écrire autre chose autour) :

Suggestions: 
- Réponse 1
- Réponse 2
- Réponse 3

3. Quand le problème est suffisamment clair, propose UN seul exercice ciblé (clair, précis et court). Termine alors ton message par cette phrase exacte :
"Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"

Important :
- Ne propose jamais de suggestions après un exercice.
- Si tu poses une question : propose 3-4 suggestions.
- Si tu proposes un exercice : ne propose rien d'autre que l'exercice + la phrase de feedback.
- Sois bienveillant, simple et pédagogue.
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
            messages=conversation
        )

        full_reply = response.choices[0].message.content.strip()

        # Chercher s'il y a des suggestions dans la réponse
        if "Suggestions:" in full_reply:
            reply_text, suggestions_block = full_reply.split("Suggestions:", 1)
            suggestions = [line.strip("- ").strip() for line in suggestions_block.strip().split("\n") if line.strip()]
        else:
            reply_text = full_reply
            suggestions = []

        return jsonify({
            "reply": reply_text.strip(),
            "suggestions": suggestions
        })

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
