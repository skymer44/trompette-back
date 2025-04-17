from openai import OpenAI
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialisation Flask
app = Flask(__name__)
CORS(app)

# Initialisation OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt système pour cadrer l'IA
SYSTEM_PROMPT = {
    "role": "system",
    "content": """Tu es un professeur de trompette expérimenté. Voici comment tu dois fonctionner :
    
1. Si l'utilisateur expose un problème, commence par lui poser UNE seule question à la fois pour mieux comprendre. Ne propose pas d'exercice tout de suite.
2. Quand tu as assez d'informations pour comprendre le problème, propose UN seul exercice clair et court.
3. Lorsque tu proposes un exercice, termine toujours par la phrase EXACTE :
"Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"

Important :
- Quand tu poses une question, fournis en plus une liste de 2 à 4 suggestions d'exemples de réponses typiques sous forme de tableau JSON.
- Quand tu proposes un exercice, NE DONNE AUCUNE suggestion supplémentaire. Juste l'exercice + la phrase de feedback.
- Utilise un ton pédagogue, encourageant et humain.
- Utilise la notation latine (do, ré, mi...) pour les notes de musique.
- Ne donne jamais d'exercice dans la même réponse qu'une question.

Format de réponse obligatoire :
{
  "reply": "ta réponse textuelle complète ici",
  "suggestions": ["réponse possible 1", "réponse possible 2", "réponse possible 3"]
}
OU
{
  "reply": "ta réponse textuelle complète ici",
  "suggestions": []
}
Ne JAMAIS oublier ce format JSON propre, même si tu n'as pas de suggestions.
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
            messages=conversation,
            response_format="json"
        )

        ai_message = response.choices[0].message.content

        return jsonify({"reply": ai_message})

    except Exception as e:
        print("Erreur serveur:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
