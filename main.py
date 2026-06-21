import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROTA DE LIMITES (Créditos no painel)
@app.get("/api/get_limit")
@app.get("/get_limit")
def get_limit():
    return {
        "credits_left": 1000,
        "period": "day",
        "monthly_limit": 5000,
        "monthly_usage": 0
    }

class PromptRequest(BaseModel):
    prompt: str

# ROTA DE GERAÇÃO REAL DE MÚSICA (Conectando com o motor do Suno/Chirp)
@app.post("/generate")
@app.post("/api/generate")
def gerar_musica(request: PromptRequest):
    try:
        # Endereço do servidor oficial que processa o Suno de forma profissional
        # (Você pode usar serviços como GoAPI, PiAPI ou criar sua própria instância da Suno-API)
        SUNO_API_URL = "https://goapi.xyz"
        
        # Cabeçalhos com o token de autorização da API de música
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": "COLE_AQUI_SUA_API_KEY_DE_MUSICA"
        }
        
        payload = {
            "prompt": request.prompt,
            "model": "chirp-v3-5", # Versão oficial de alta qualidade do Suno
            "tags": "gospel, r&b, emotional",
            "title": "Nova Composição"
        }
        
        response = requests.post(SUNO_API_URL, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Erro ao chamar o motor Suno.")
            
        dados_suno = response.json()
        
        # Retorna os dados com os links de áudio .mp3 e imagem reais gerados pelo Suno
        return dados_suno.get("data", [])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
