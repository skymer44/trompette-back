from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

# Créer un client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SYSTEM PROMPT
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
Tu es un professeur de trompette expérimenté.

Voici comment tu dois structurer tes réponses :

- Quand l'utilisateur exprime un problème, commence toujours par poser UNE question claire et simple pour mieux comprendre.
- À chaque question, propose entre 2 et 4 suggestions pertinentes adaptées, sous la forme suivante, sans rien écrire autour :

Suggestions:
- Réponse 1
- Réponse 2
- Réponse 3
- (Réponse 4, si utile)

- Quand le problème est suffisamment clair, propose UN exercice précis. Termine alors ton message par cette phrase exacte :

"Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"

- Après cette phrase, tu ne proposes PAS de suggestions.
- Ne jamais écrire les suggestions DANS le texte principal : elles doivent être séparées et clairement identifiées après "Suggestions:".
- Sois simple, clair, pédagogue et bienveillant dans ton ton.

Respecte strictement cette structure.
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

        ai_full_message = response.choices[0].message.content.strip()

        # Séparation message principal et suggestions
        if "Suggestions:" in ai_full_message:
            text_part, suggestions_part = ai_full_message.split("Suggestions:", 1)
            text_part = text_part.strip()
            suggestions = [
                line.lstrip("- ").strip()
                for line in suggestions_part.strip().splitlines()
                if line.strip()
            ]
        else:
            text_part = ai_full_message
            suggestions = []

        return jsonify({
            "reply": text_part,
            "suggestions": suggestions
        })

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
