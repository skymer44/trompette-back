from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import logging
from openai import OpenAI
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SYSTEM_PROMPT = """Tu es un professeur de trompette expérimenté et bienveillant. Ta mission est d'aider les élèves à progresser en comprenant précisément leurs difficultés avant de proposer des solutions.

RÈGLES ABSOLUES À RESPECTER POUR CHAQUE RÉPONSE :

1. FORMAT DE RÉPONSE (TOUJOURS LE MÊME) :
Réponds uniquement en JSON avec cette structure exacte :
{
  "reply": "ton message",
  "suggestions": ["suggestion 1", "suggestion 2", ...],
  "is_exercise": false/true
}

2. DEUX TYPES DE RÉPONSES POSSIBLES :

   A) QUESTION À L'ÉLÈVE (is_exercise: false)
      - Objectif : Comprendre la difficulté précise de l'élève.
      - "reply" doit contenir UNE question courte et claire.
      - "suggestions" doit proposer entre 2 et 4 choix courts maximum.
      - Ne JAMAIS donner de conseil ou d'exercice à cette étape.

   B) PROPOSITION D'UN EXERCICE (is_exercise: true)
      - Objectif : Aider l'élève à résoudre son problème.
      - "suggestions" DOIT ÊTRE une liste vide [].
      - "reply" DOIT être structuré en DEUX PARTIES OBLIGATOIRES :
        1) Une description claire de l'exercice.
        2) Puis TERMINER EXCLUSIVEMENT par cette phrase, mot pour mot :
           Est-ce que cet exercice t'a aidé ? Peux-tu me dire si ça fonctionne pour toi ou si tu ressens encore une difficulté ?

   IMPORTANT : 
   - Cette phrase finale est OBLIGATOIRE pour TOUT exercice.
   - NE PAS ajouter d'autres phrases après cette question.

3. RÈGLES DE FORMATTING STRICTES :
   - Aucun texte hors du JSON.
   - Jamais de formatage Markdown dans "reply".
   - Pas d'introduction, pas d'excuse, pas de message de conclusion.
   - Les suggestions doivent être adaptées à la question posée.

4. SI TU REÇOIS UN FEEDBACK APRÈS UN EXERCICE :
   - Ne pas reposer de nouvelle question.
   - Proposer directement un nouvel exercice ou une variante si nécessaire.

Ton objectif est de rester simple, bienveillant et rigoureux.
Respecte TOUTES ces règles sans exception.
"""

def validate_openai_response(response: str) -> Optional[Dict[str, Any]]:
    try:
        parsed = json.loads(response)
        if not all(key in parsed for key in ["reply", "suggestions", "is_exercise"]):
            logger.error(f"Missing required fields in response: {parsed}")
            return None
        if not isinstance(parsed["reply"], str) or \
           not isinstance(parsed["suggestions"], list) or \
           not isinstance(parsed["is_exercise"], bool):
            logger.error(f"Invalid field types in response: {parsed}")
            return None
        if parsed["is_exercise"] and len(parsed["suggestions"]) != 0:
            logger.error(f"Exercise response contains suggestions: {parsed}")
            return None
        if not parsed["is_exercise"] and not (2 <= len(parsed["suggestions"]) <= 4):
            logger.error(f"Invalid number of suggestions for question: {parsed}")
            return None
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error validating response: {e}")
        return None

def get_openai_response(messages: list, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting OpenAI request (attempt {attempt + 1}/{max_retries})")

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            logger.info(f"OpenAI raw response: {content}")

            validated_response = validate_openai_response(content)
            if validated_response:
                return validated_response

            logger.warning(f"Invalid response format (attempt {attempt + 1})")

        except Exception as e:
            logger.error(f"OpenAI API error (attempt {attempt + 1}): {str(e)}")

    return None

def create_error_response(message: str = "Une erreur est survenue. Veuillez réessayer.") -> Dict[str, Any]:
    return {
        "reply": message,
        "suggestions": [],
        "is_exercise": False
    }

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or not isinstance(data.get('messages'), list):
            logger.warning("Invalid request: missing messages list")
            return jsonify(create_error_response("Format de requête invalide")), 400

        user_id = data.get('user_id')
        messages = data['messages']

        logger.info(f"Received chat request with {len(messages)} messages")

        valid_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
            if isinstance(msg, dict)
            and "role" in msg
            and "content" in msg
            and isinstance(msg["content"], str)
            and msg["content"].strip()
        ]

        conversation = [{"role": "system", "content": SYSTEM_PROMPT}] + valid_messages

        response = get_openai_response(conversation)
        if not response:
            logger.error("Failed to get valid response from OpenAI")
            return jsonify(create_error_response()), 500

        logger.info("Sending successful response to client")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify(create_error_response()), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port)
