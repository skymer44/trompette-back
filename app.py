from openai import OpenAI
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt système adapté pour conserver le contexte
system_prompt = {
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

⚠️ Tu dois te souvenir de toute la conversation précédente pour progresser étape par étape. N’oublie pas ce qui a été dit avant.
Ne recommence pas la discussion depuis le début.
"""
}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_messages = data.get("messages", [])

    # Construction de l’historique complet avec le prompt système
    messages = [system_prompt] + user_messages

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Erreur serveur : {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
