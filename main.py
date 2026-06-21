import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI()

# Permite conexões do seu site sem bloqueios de segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)

class PromptRequest(BaseModel):
    prompt: str

# 1. ROTA DE LIMITES (O que o seu site pede primeiro)
@app.get("/api/get_limit")
@app.get("/get_limit")
def get_limit():
    # Fingimos para o seu site que você tem créditos infinitos livres
    return {
        "credits_left": 1000,
        "period": "day",
        "monthly_limit": 5000,
        "monthly_usage": 0
    }

# 2. ROTA DE GERAÇÃO CORRIGIDA
@app.post("/generate")
@app.post("/api/generate")
def gerar_musica(request: PromptRequest):
    try:
        # Gera o conteúdo usando o modelo estável do Google
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Gere a letra de uma musica com base nisto: {request.prompt}"
        )
        
        # Estrutura simulada do Suno para o seu site aceitar o resultado visualmente
        return [
            {
                "id": "gemini-task-1",
                "video_url": "",
                "audio_url": "",
                "image_url": "https://unsplash.com",
                "title": "Musica Gerada",
                "lyric": response.text,
                "status": "complete"
            }
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
