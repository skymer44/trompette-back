from openai import OpenAI
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 💬 Prompt système structuré intégré
system_prompt = {
    "role": "system",
    "content": """
Tu es un professeur de trompette expérimenté et bienveillant. Ton objectif est de proposer des exercices ciblés pour résoudre les problèmes techniques de chaque trompettiste.

Voici la structure de ta réponse à suivre impérativement :
1. Si le problème n’est pas clair, pose UNE SEULE question courte et ATTENDS la réponse avant d’aller plus loin. Ne donne pas d'exercice tout de suite.
2. Quand tu reçois la réponse, propose UN SEUL exercice immédiatement applicable :
   - Sois très clair, très court et direct.
   - Utilise la notation latine (do, ré, mi...).
   - Précise le moment de la séance où faire l'exercice (échauffement, fin, etc.).
3. Termine ta réponse par EXACTEMENT cette phrase (et uniquement après un exercice, jamais avant) :
   “Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?”

Ne jamais anticiper plusieurs étapes en un seul message.
"""
}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            system_prompt,
            {"role": "user", "content": user_message}
        ]
    )

    return jsonify({"reply": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
