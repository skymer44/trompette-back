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

EXEMPLES DE FORMAT CORRECT :

Exemple 1 (Oui/Non) :
Est-ce que tu ressens une fatigue musculaire après avoir joué ?
Suggestions:
- Oui
- Non

Exemple 2 (Plusieurs choix) :
À quel moment de la journée pratiques-tu généralement ?
Suggestions:
- Le matin
- L'après-midi
- Le soir
- À des horaires variables

Exemple 3 (Exercice) :
Voici un exercice pour améliorer ton endurance : [description de l'exercice]
Est-ce que cet exercice t'a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?"""

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

        # Check if this is a question (has suggestions) or an exercise (has feedback request)
        has_feedback_request = "Est-ce que cet exercice t'a aidé ?" in ai_message
        has_suggestions = "Suggestions:" in ai_message

        if has_suggestions and not has_feedback_request:
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

            # Validate Yes/No suggestions
            if len(suggestions) == 2 and suggestions[0].lower() in ['oui', 'yes'] and suggestions[1].lower() in ['non', 'no']:
                suggestions = ['Oui', 'Non']  # Normalize to French
            elif 2 <= len(suggestions) <= 4:
                pass  # Keep suggestions as is
            else:
                print("\n=== Warning: Invalid number of suggestions ===")
                print(f"Found {len(suggestions)} suggestions: {suggestions}")

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
