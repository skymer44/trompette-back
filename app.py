from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SYSTEM_PROMPT = """Tu es un professeur de trompette expérimenté et bienveillant. Ta mission est de comprendre précisément le problème de l'élève avant de proposer une solution.

RÈGLES ABSOLUES à suivre :

1. PREMIÈRE ÉTAPE - COMPRENDRE (OBLIGATOIRE)
   - Quand l'utilisateur décrit un problème, pose TOUJOURS une seule question courte et précise
   - But unique : comprendre exactement la difficulté rencontrée
   - Ne JAMAIS donner de conseil ou d'exercice à cette étape
   - Ne JAMAIS orienter vers une solution
   - Juste poser UNE question pertinente

2. FORMAT DES SUGGESTIONS (ULTRA CRITIQUE)
   TOUJOURS respecter ce format exact :

   Pour une réponse Oui/Non :
   [Ta question]
   Suggestions:
   - Oui
   - Non

   Pour les autres cas :
   [Ta question]
   Suggestions:
   - Suggestion 1
   - Suggestion 2
   - Suggestion 3
   [2 à 4 suggestions maximum]

   RÈGLES DE FORMATAGE STRICTES :
   - Le mot "Suggestions:" DOIT être sur une ligne seule
   - CHAQUE suggestion DOIT commencer par "- "
   - UNE SEULE suggestion par ligne
   - JAMAIS de tirets ou séparateurs entre les suggestions
   - JAMAIS de suggestions sur la même ligne

3. EXERCICE (UNIQUEMENT QUAND LE PROBLÈME EST CLAIR)
   - Propose UN SEUL exercice ciblé
   - Termine EXACTEMENT par :
   "Est-ce que cet exercice t'a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"
   - JAMAIS de suggestions après un exercice

"""

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({'error': 'No messages provided'}), 400

        # Validate and format the conversation history
        valid_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in data["messages"]
            if isinstance(msg, dict)
            and "role" in msg
            and "content" in msg
            and isinstance(msg["content"], str)
            and msg["content"].strip() != ""
        ]

        # Add system prompt at the beginning
        conversation = [{"role": "system", "content": SYSTEM_PROMPT}] + valid_messages

        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation
        )

        ai_message = response.choices[0].message.content.strip()

        # Initialize suggestions list
        suggestions = []

        # Check if this is a question (has suggestions) or an exercise (has feedback request)
        has_feedback_request = "Est-ce que cet exercice t'a aidé ?" in ai_message
        has_suggestions = "Suggestions:" in ai_message

        if has_suggestions and not has_feedback_request:
            # Split the message and extract suggestions
            parts = ai_message.split("Suggestions:")
            ai_message = parts[0].strip()

            # Improved parsing to split multiple suggestions even if they are on the same line
            suggestion_text = parts[1].strip()
            raw_suggestions = []
            for line in suggestion_text.split('\n'):
                if line.strip():
                    # Split again if multiple '- ' appear in the same line
                    parts_line = line.split('- ')
                    for part in parts_line:
                        part = part.strip()
                        if part:
                            raw_suggestions.append(part)
            suggestions = raw_suggestions

            # Normalize if it's a yes/no question
            if len(suggestions) == 2 and suggestions[0].lower() in ['oui', 'yes'] and suggestions[1].lower() in ['non', 'no']:
                suggestions = ['Oui', 'Non']

        # Format the response
        response_data = {
            'reply': ai_message,
            'suggestions': suggestions
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"\n=== Error ===\n{str(e)}\n============\n")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
