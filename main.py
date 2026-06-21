import os
import base64
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

# 1. ROTA DE LIMITES (Garante os créditos no painel)
@app.get("/api/get_limit")
@app.get("/get_limit")
def get_limit():
    return {
        "credits_left": 1000,
        "period": "day",
        "monthly_limit": 5000,
        "monthly_usage": 0
    }

# 2. ROTA DE GERAÇÃO COM O MOTOR DE MÚSICA LYRIA
@app.post("/generate")
@app.post("/api/generate")
def gerar_musica(request: PromptRequest):
    try:
        print(f"Enviando solicitação de áudio para o Lyria: {request.prompt}")
        
        # Faz a chamada oficial para o modelo de áudio generativo do Google
        response = client.models.generate_content(
            model="lyria-3-pro-preview",
            contents=f"Crie uma musica completa com base nisto: {request.prompt}"
        )
        
        audio_base64 = ""
        letra_gerada = "Letra indisponível para este estilo."
        
        # Varre a resposta do Google procurando pelos bytes de som e texto da letra
        for part in response.parts:
            if part.inline_data:
                # Transforma os bytes do arquivo de som em um formato legível por navegadores web
                audio_base64 = base64.b64encode(part.inline_data.data).decode('utf-8')
            if part.text:
                letra_gerada = part.text

        if not audio_base64:
            raise HTTPException(status_code=500, detail="O servidor gerou a resposta, mas nao enviou os dados de som.")

        # Criamos o link direto em memória (Data URI) para o player do seu site tocar na hora
        url_audio_final = f"data:audio/mp3;base64,{audio_base64}"
        
        # Devolve os dados estruturados no formato do Suno, injetando o áudio real do Lyria
        return [
            {
                "id": "lyria-task-generation",
                "video_url": "",
                "audio_url": url_audio_final,
                "image_url": "https://unsplash.com",
                "title": f"Lyria - {request.prompt[:15]}...",
                "lyric": letra_gerada,
                "status": "complete"
            }
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
