import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# O CORS permite que o seu site do Arcada App consiga conversar com esse backend
CORS(app)

# O Render vai ler a chave secreta que vamos configurar lá no painel deles
AIML_API_KEY = os.getenv("AIML_API_KEY")

@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.json
        prompt = data.get('prompt')
        tags = data.get('tags', '')
        make_instrumental = data.get('make_instrumental', False)

        # Dados que a AIML API pede para gerar a música
        payload = {
            "model": "suno/v3.5",
            "prompt": prompt,
            "tags": tags,
            "make_instrumental": make_instrumental
        }

        headers = {
            "Authorization": f"Bearer {AIML_API_KEY}",
            "Content-Type": "application/json"
            }

        # Faz o pedido de geração para a API externa
        response = requests.post(
            "https://aimlapi.com", 
            json=payload, 
            headers=headers
        )
        
        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/music-status/<task_id>', methods=['GET'])
def music_status(task_id):
    try:
        headers = {"Authorization": f"Bearer {AIML_API_KEY}"}
        
        # Pergunta para a API se a música com esse ID já ficou pronta
        response = requests.get(
            f"https://aimlapi.com{task_id}", 
            headers=headers
        )
        
        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Configuração necessária para o Render conseguir rodar o projeto
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
