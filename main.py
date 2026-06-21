import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI()

# Permite que o seu site converse com essa API sem bloqueios de segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pega a chave que configuraremos direto no painel do servidor
API_KEY = os.getenv("GEMINI_API_KEY", "SUA_CHAVE_AQUI")
client = genai.Client(api_key=API_KEY)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/gerar-musica")
def gerar_musica(request: PromptRequest):
    try:
        # Modelo oficial que testamos e funcionou sem erros
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Gere a letra de uma musica com base neste prompt: {request.prompt}"
        )
        return {"sucesso": True, "letra": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
