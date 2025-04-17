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

SYSTEM_PROMPT = """Tu es un professeur de trompette expérimenté.

Voici comment tu dois répondre :

1. Quand l'utilisateur décrit un problème, commence par poser UNE seule question courte et simple pour mieux comprendre.

2. Quand tu poses une question :
   - Si la réponse logique est OUI ou NON, propose uniquement ces deux choix.
   - Sinon, propose entre 2 et 4 suggestions variées adaptées.
   - Sépare toujours les suggestions du texte principal avec "Suggestions:"

3. Quand le problème est suffisamment clair, propose UN SEUL exercice ciblé.
   - Termine alors par EXACTEMENT cette phrase :
   "Est-ce que cet exercice t'a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"
   - Ne propose JAMAIS de suggestions après un exercice.

Important :
- Sois simple, clair, pédagogue et bienveillant.
- Une seule question à la fois.
- Suggestions toujours séparées du texte.
- Pas de suggestions après un exercice."""

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
            messages=conversation
        )

        # Extract the response text
        ai_message = response.choices[0].message.content.strip()

        # Log the response from OpenAI
        print("\n=== Response from OpenAI ===")
        print(ai_message)

        # Initialize suggestions list
        suggestions = []

        # Check if the message contains suggestions
        if "Suggestions:" in ai_message and "Est-ce que cet exercice t'a aidé ?" not in ai_message:
            # Split the message and extract suggestions
            parts = ai_message.split("Suggestions:")
            ai_message = parts[0].strip()
            
            # Parse suggestions, removing empty lines and bullet points
            suggestion_text = parts[1].strip()
            suggestions = [
                line.strip().lstrip('- ').strip()
                for line in suggestion_text.split('\n')
                if line.strip() and line.strip() != '-'
            ]

        # Format the response
        response_data = {
            'reply': ai_message,
            'suggestions': suggestions
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
