import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Extra

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pega o token da AIMLAPI salvo no painel do Render
API_KEY = os.getenv("SUNO_API_KEY", "")

# 1. ROTA DE CREDITOS (Garante os créditos livres no painel)
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
    class Config:
        extra = Extra.allow

# 2. ROTA DE GERACAO ALINHADA COM A DOCUMENTAÇÃO V2 DA AIMLAPI
@app.post("/generate")
@app.post("/api/generate")
@app.post("/custom_generate")
@app.post("/api/custom_generate")
def gerar_musica(request: PromptRequest):
    try:
        # URL oficial v2 da AIMLAPI para geração de mídias de áudio
        URL_AIML = "https://api.aimlapi.com/v2/generate/audio"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Estrutura exata exigida pelo servidor deles para rodar o Suno AI
        payload = {
            "model": "suno/chirp-v3-5",
            "prompt": request.prompt
        }
        
        response = requests.post(URL_AIML, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Erro AIMLAPI: {response.text}")
            
        dados_recebidos = response.json()
        
        # Formata a resposta para o player do seu site ler os links de áudio de primeira
        if isinstance(dados_recebidos, list):
            return dados_recebidos
        elif "data" in dados_recebidos:
            return dados_recebidos["data"]
            
        return [dados_recebidos]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
