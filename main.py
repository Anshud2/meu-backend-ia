import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Extra

app = FastAPI()

# Permite conexões do seu site de música sem bloqueios de segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pega a chave secreta cadastrada no seu painel do Render
API_KEY = os.getenv("SUNO_API_KEY", "")

# 1. ROTA DE CREDITOS (Garante o funcionamento estável do painel)
@app.get("/api/get_limit")
@app.get("/get_limit")
def get_limit():
    return {
        "credits_left": 1000,
        "period": "day",
        "monthly_limit": 5000,
        "monthly_usage": 0
    }

# Modelo flexível para aceitar tags, título ou letras do Modo Customizado
class PromptRequest(BaseModel):
    prompt: str
    class Config:
        extra = Extra.allow

# 2. ROTAS DE GERACAO CONECTADAS COM A AIMLAPI
@app.post("/generate")
@app.post("/api/generate")
@app.post("/custom_generate")
@app.post("/api/custom_generate")
def gerar_musica(request: PromptRequest):
    try:
        # URL oficial da API da AIMLAPI para geração com Suno AI v3.5
        URL_AIML = "https://aimlapi.com"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Dados organizados no formato exato que a documentação deles exige
        payload = {
            "prompt": request.prompt,
            "model": "suno-v3.5",
            "custom": False
        }
        
        # Faz o envio seguro do prompt para a AIMLAPI
        response = requests.post(URL_AIML, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Erro AIMLAPI: {response.text}")
            
        dados_recebidos = response.json()
        
        # Retorna a lista de mídias estruturada para o player do seu site ler
        if isinstance(dados_recebidos, list):
            return dados_recebidos
            
        return dados_recebidos.get("data", [dados_recebidos])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
