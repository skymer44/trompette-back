Mon application utilise la bibliothèque openai pour interagir avec l’API d’OpenAI. Je souhaite que le projet utilise **exactement la version 1.75.0** de cette bibliothèque, qui est la dernière version stable publiée.

**Objectifs** :

1. **Mettre à jour les dépendances** :
    - Dans le fichier requirements.txt, spécifier :

openai==1.75.0

1. **Adapter le code pour utiliser correctement la dernière version de OpenAI** :
    - Importer et initialiser le client OpenAI comme suit :

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

1. **Utiliser obligatoirement le modèle GPT-4o** :
    - Quand tu écris un appel à l’API dans le backend, la valeur du modèle doit être "gpt-4o", comme ceci :

response = client.chat.completions.create(
model="gpt-4o",
messages=[
{"role": "system", "content": "You are a helpful assistant."},
{"role": "user", "content": "Bonjour, j'ai une question sur la trompette..."},
]
)

1. **Respecter la structure de communication** :
    - Vérifie que le front-end envoie bien à chaque appel les deux informations nécessaires :
        - messages (tableau d’objets { role: “user” / “assistant”, content: “…” })
        - user_id (identifiant utilisateur unique pour associer les conversations)
    - Si jamais l’utilisateur n’est pas connecté, un user_id temporaire doit être généré côté front-end pour pouvoir quand même discuter.
2. **Supprimer tout paramètre obsolète** :
    - Ne pas utiliser de paramètre proxies ou d’autres paramètres non pris en charge dans la version 1.75.0.
    - Corriger si besoin les autres appels pour qu’ils soient compatibles avec la documentation officielle OpenAI v1.75.0.
3. **Autres contraintes** :
    - Assure-toi que le code est totalement fonctionnel pour Python 3.11.
    - L’application doit continuer à fonctionner normalement après migration.
    - Aucun avertissement de dépréciation ne doit apparaître dans les logs.
