from openai import OpenAI
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
           
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return jsonify({"reply": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
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
