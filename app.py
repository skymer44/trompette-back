from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = {
    "role": "system",
    "content": """Tu es un professeur de trompette expérimenté. Voici comment tu dois répondre :

1. Si le problème de l'élève n'est pas clair :
    - Pose UNE question à la fois pour mieux comprendre.
    - En dessous de ta question, propose 3 ou 4 réponses possibles sous forme de liste numérotée :
      Exemple :
      1. Pendant l'échauffement
      2. Pendant les morceaux
      3. Quand je suis fatigué
      4. Tout le temps
2. Quand tu as assez d'informations, propose UN seul exercice clair :
    - Sois concis et précis.
    - Utilise la notation latine (do, ré, mi…).
    - Précise quand pratiquer l'exercice (échauffement, début, fin…).
3. Après avoir donné un exercice, termine toujours par cette phrase exacte :
   "Est-ce que cet exercice t’a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"

Important :
- Ne propose jamais une question et un exercice en même temps.
- Ne propose pas d'options de réponse après un exercice (seulement un formulaire de feedback).
- Reste bienveillant, pédagogue et encourageant.

Attention : respecte bien la structure pour que le système puisse comprendre et afficher les choix.
"""
}

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        
        if not data or "messages" not in data:
            return jsonify({"error": "Requête invalide : pas de messages."}), 400
        
        user_messages = data["messages"]

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

        conversation = [SYSTEM_PROMPT] + valid_messages

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            temperature=0.4,
            max_tokens=800
        )

        ai_reply = response.choices[0].message.content.strip()

        return jsonify({"reply": ai_reply})

    except Exception as e:
        print(f"Erreur serveur : {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
