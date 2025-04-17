from openai import OpenAI
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialiser OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt système corrigé
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
Tu es un professeur de trompette expérimenté. Voici exactement comment tu dois te comporter :

1. Si le problème n'est pas encore clair ou précis, POSE UNE SEULE QUESTION.
    ➔ Après ta question, propose TOUJOURS entre 2 et 4 réponses possibles sous forme de texte court, en français, adaptées au contexte.
    ➔ Même si ce n'est pas évident, invente les réponses les plus logiques et naturelles possibles, mais sans jamais inventer du faux.

2. Si tu as compris clairement le problème, PROPOSE UN EXERCICE.
    ➔ Donne un seul exercice clair, concis et ciblé.
    ➔ Utilise la notation latine pour les notes de musique (do, ré, mi…).
    ➔ Indique dans quel moment le pratiquer (échauffement, début, fin...).

3. Après avoir donné un exercice, termine TOUJOURS ton message par cette phrase EXACTE :
"Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"

Rappels importants :
- Ne pose jamais une question ET un exercice dans le même message.
- Ne propose jamais zéro ni plus de 4 suggestions après une question.
- Si la réponse libre est meilleure pour l'utilisateur, il pourra toujours écrire sa réponse manuellement.
- Sois toujours bienveillant, encourageant et professionnel.
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
            if isinstance(msg, dict) and "role" in msg and "content" in msg and isinstance(msg["content"], str) and msg["content"].strip() != ""
        ]

        if not valid_messages:
            return jsonify({"error": "Aucun message utilisateur valide reçu."}), 400

        # Construire la conversation avec le system prompt
        conversation = [SYSTEM_PROMPT] + valid_messages

        # Appeler OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            temperature=0.5  # Optionnel : pour des réponses plus naturelles
        )

        reply_content = response.choices[0].message.content.strip()

        # Détecter s'il y a des suggestions encadrées (markdown liste ou numérotation simple)
        suggestions = []
        lines = reply_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("- "):
                suggestion = line[line.find(' ')+1:].strip()
                suggestions.append(suggestion)

        # Limiter à 2-4 suggestions seulement
        if len(suggestions) < 2 or len(suggestions) > 4:
            suggestions = []

        return jsonify({
            "reply": reply_content,
            "suggestions": suggestions
        })

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
