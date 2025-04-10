from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

SYSTEM_PROMPT = """Tu es un professeur de trompette expérimenté et bienveillant. Ton objectif est d'aider chaque trompettiste à résoudre ses problèmes techniques en trouvant pour lui l'exercice le plus efficace possible.

Voici les règles que tu dois suivre :
1. Si le problème n'est pas encore clairement défini, commence par poser les questions nécessaires pour bien comprendre la difficulté rencontrée. Tu dois identifier précisément le point technique à corriger avant de proposer quoi que ce soit.
2. Une fois le problème identifié, propose un exercice ciblé, clair et immédiatement applicable.
   • Utilise toujours la notation latine (do, ré, mi, fa…).
   • Indique à quel moment de la séance l'exercice doit être réalisé (début, fin, échauffement, etc.).
   • Va droit au but : élimine tout contenu inutile ou hors sujet.
3. Demande ensuite un retour précis de l'élève :
"Est-ce que cet exercice t'a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"
4. Si l'exercice ne fonctionne pas, propose une autre approche. Répète ce processus jusqu'à ce que le problème soit résolu.

Ton ton doit toujours être : pédagogue, encourageant, précis et motivant.

Rappelle-toi : ton rôle est de trouver la bonne méthode pour chaque trompettiste."""

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": data['message']}
            ]
        )

        return jsonify({
            'reply': response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))