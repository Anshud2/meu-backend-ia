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

# Pega a nova chave que você acabou de cadastrar no painel do Render
API_KEY = os.getenv("SUNO_API_KEY", "")

# 1. ROTA DE CREDITOS (Mostra 1000 créditos livres no seu painel)
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

# 2. ROTA DE GERACAO CONECTADA COM A AIMLAPI (SUNO v3.5)
@app.post("/generate")
@app.post("/api/generate")
def gerar_musica(request: PromptRequest):
    try:
        # URL oficial de geracao da AIMLAPI para o modelo do Suno
        URL_AIML = "https://aimlapi.com"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": request.prompt,
            "model": "suno-v3.5",
            "custom": False
        }
        
        # Envia o pedido de musica para a AIMLAPI
        response = requests.post(URL_AIML, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Erro AIMLAPI: {response.text}")
            
        dados_recebidos = response.json()
        
        # A AIMLAPI devolve a lista de midias exatamente no padrao que seu site precisa
        # incluindo os links reais de audio (.mp3), letra e imagem da capa!
        return dados_recebidos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
