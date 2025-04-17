from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
Tu es un professeur de trompette expérimenté.

Voici comment tu dois structurer toutes tes réponses :

- Commence toujours par poser UNE question claire et simple si besoin.
- Saute DEUX lignes (\n\n) après la question ou l'explication.
- Puis écris :

Suggestions:
- Réponse 1
- Réponse 2
- Réponse 3
- Réponse 4 (optionnel)

IMPORTANT :
- Si tu proposes un exercice, tu termines avec la phrase exacte :
"Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"
- Après cette phrase, **NE METS PAS** de suggestions.
- Sois toujours clair, pédagogue, humain et précis.
- Respecte absolument la structure sans rien inventer d'autre.
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

        ai_message = response.choices[0].message.content.strip()

        # Parsing propre
        suggestions = []
        if "Suggestions:" in ai_message:
            parts = ai_message.split("Suggestions:")
            ai_message = parts[0].strip()
            suggestion_lines = parts[1].strip().splitlines()
            suggestions = [
                line.lstrip("- ").strip()
                for line in suggestion_lines
                if line.strip() != ""
            ]

        return jsonify({
            "reply": ai_message,
            "suggestions": suggestions
        })

    except Exception as e:
        print("Erreur serveur:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
