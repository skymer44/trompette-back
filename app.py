# Nouveau backend ultra fiable avec JSON strict

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

# Nouveau SYSTEM PROMPT strict
SYSTEM_PROMPT = """
Tu es un professeur de trompette expérimenté et bienveillant.

Ta mission est de comprendre précisément le problème de l'élève avant de proposer une solution.

RÈGLES ABSOLUES :
1. Si l'utilisateur expose un problème, pose UNE seule question courte pour mieux comprendre.
2. Si une question attend une réponse Oui/Non, propose uniquement "Oui" et "Non".
3. Sinon, propose entre 2 et 4 suggestions pertinentes.
4. Si le problème est compris, propose UN seul exercice et termine EXACTEMENT par :
   "Est-ce que cet exercice t'a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"

IMPORTANT : Tu dois TOUJOURS répondre sous forme d'un JSON strict. Pas de texte autour, uniquement du JSON.

Format attendu :
{
  "reply": "ta question ou la proposition d'exercice",
  "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
  "is_exercise": false
}

Si c'est un exercice, "is_exercise" doit être à true, et "suggestions" doit être une liste vide [].
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

        # Log the conversation being sent to OpenAI
        print("\n=== Sending to OpenAI ===")
        for msg in conversation:
            print(f"{msg['role'].upper()}: {msg['content'][:100]}...")

        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            response_format="json"  # Force OpenAI à répondre en JSON
        )

        # Parse the JSON response
        ai_response = response.choices[0].message.content.strip()
        parsed_response = eval(ai_response)  # Convert JSON string to Python dict

        # Format final output
        response_data = {
            'reply': parsed_response.get('reply', ''),
            'suggestions': parsed_response.get('suggestions', []),
            'is_exercise': parsed_response.get('is_exercise', False)
        }

        # Log the final formatted response
        print("\n=== Final Response ===")
        print(response_data)
        print("==================\n")

        return jsonify(response_data)

    except Exception as e:
        print(f"\n=== Error ===\n{str(e)}\n============\n")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
