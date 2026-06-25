 ```
   MUSIC_PROVIDER = huggingface
   HF_API_KEY = hf_seu_token_aqui
 ```

 E remova (ou deixe vazia) a AIML_API_KEY.

 ### 3️⃣ Substitua o app.py

 Substitua o conteúdo de https://github.com/Anshud2/meu-backend-ia/blob/main/app.py pelo novo arquivo que salvei em
 C:\Users\anshu\Downloads\app_free_hf.py.

 Localmente:

 ```bash
   cd seu-repo
   # (copia o conteudo de app_free_hf.py pra app.py)
   git add app.py
   git commit -m "Migra para Hugging Face (free tier para testes)"
   git push origin main
 ```

 ### 4️⃣ Aguarde o redeploy (~2 min) e teste

 Endpoint pra ver o status:

 ```bash
   curl https://meu-backend-ia-2.onrender.com/api/providers
 ```

 Endpoint pra gerar música:

 ```bash
   curl -X POST https://meu-backend-ia-2.onrender.com/api/generate-music \
     -H "Content-Type: application/json" \
     -d '{"prompt":"lo-fi hip hop relaxante com piano e batida suave","instrumental":true}'
 ```

 Resposta esperada:

 ```json
   {
     "id": "hf_1719335...",
     "status": "completed",
     "audio_url": "/api/audio/hf_1719335....mp3",
     "provider": "huggingface"
   }
 ```

 Aí é só acessar https://meu-backend-ia-2.onrender.com/api/audio/hf_xxxxx.mp3 pra ouvir! 🎵

 ────────────────────────────────────────────────────────────────────────────────

 🆘 Se der erro 503 na primeira tentativa

 É normal! O HF coloca o modelo "pra dormir" quando ninguém usa. O backend já trata isso retornando uma mensagem clara
 dizendo "tente em ~30s". Basta repetir a request 1-2 vezes.

 ────────────────────────────────────────────────────────────────────────────────

 Quer que eu te ajude com mais alguma coisa? Por exemplo:

 1. Atualizar o index.html pra funcionar bem com o HF (sem letra)?
 2. Adicionar fallback automático — se HF falhar, tenta Replicate (quando você colocar créditos depois)?
 3. Te guiar passo a passo no git push se tiver dúvida?


 me explica passo a  passo


 Beleza! Vou te guiar passo a passo como se fosse a primeira vez. Vou dividir em blocos bem pequenos.

 ────────────────────────────────────────────────────────────────────────────────

 📍 PASSO 1 — Revogar a chave AIMLAPI que vazou

 Você postou a chave 0695e6883389e249cfd4ed75bc3f11ff aqui no chat. Mesmo que a conta esteja sem créditos, é bom
 revogar por segurança.

 1. Abra no navegador: https://aimlapi.com/app
 2. Faça login com sua conta
 3. Vá em API Keys (no menu lateral esquerdo)
 4. Você vai ver a chave 0695e688... listada
 5. Clique nos 3 pontinhos ao lado dela ou no botão Delete/Revoke
 6. Confirme a exclusão

 ✅ Pronto. Agora ninguém mais pode usar essa chave.

 ────────────────────────────────────────────────────────────────────────────────

 📍 PASSO 2 — Criar conta gratuita no Hugging Face

 1. Abra: https://huggingface.co
 2. Clique em Sign Up (canto superior direito)
 3. Crie a conta com email + senha (ou entre com Google/GitHub se preferir)
 4. Confirme o email se pediu
 5. Faça login

 ✅ Conta criada.

 ────────────────────────────────────────────────────────────────────────────────

 📍 PASSO 3 — Gerar o token gratuito

 1. Já logado, abra direto: https://huggingface.co/settings/tokens
 2. Clique no botão "+ Create new token"
 3. Em Type, escolha Read (esse é o gratuito)
 4. Em Name, digite algo como suno-studio
 5. Clique em Generate a token
 6. Vai aparecer uma string tipo hf_AbCdEf123456... — COPIE ELA e cole num bloco de notas
     - ⚠️ O HF só mostra essa string uma vez. Se perder, tem que gerar outra.

 ✅ Token salvo no bloco de notas.

 Exemplo de como o token se parece:

 ```
   hf_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
 ```

 ────────────────────────────────────────────────────────────────────────────────

 📍 PASSO 4 — Atualizar o app.py no seu computador

 Você tem duas opções. Vou pela mais fácil:

 ### Opção A — Download direto (mais fácil)

 1. Abre o Explorador de Arquivos do Windows
 2. Vai em C:\Users\anshu\Downloads
 3. Procura o arquivo app_free_hf.py que eu criei (16.938 bytes)
 4. Renomeia ele de app_free_hf.py para app.py
     - Clique direito → Renomear → apaga o _free_hf → fica só app.py
 5. Abre o arquivo app.py com o Bloco de Notas (clique direito → Abrir com → Bloco de Notas)
 6. Dá um Ctrl+A (selecionar tudo) e Ctrl+C (copiar)

 ### Opção B — Copiar pelo navegador (se preferir)

 1. Vou colar o conteúdo completo aqui embaixo e você copia pro seu editor

 ```python
   import os
   import time
   import logging
   import requests
   from flask import Flask, request, jsonify, send_from_directory
   from flask_cors import CORS

   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s [%(levelname)s] %(message)s",
   )
   log = logging.getLogger("suno-studio")

   app = Flask(__name__, static_folder=".", static_url_path="")

   CORS(app, resources={r"/api/*": {"origins": "*"}})

   # ============================================================
   # CONFIGURACAO DE PROVIDERS
   # ============================================================
   MUSIC_PROVIDER = os.getenv("MUSIC_PROVIDER", "huggingface").lower()

   HF_API_KEY = os.getenv("HF_API_KEY", "")
   HF_MUSIC_MODEL = os.getenv("HF_MUSIC_MODEL", "facebook/musicgen-large")
   HF_BASE = "https://api-inference.huggingface.co/models"

   REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY", "")
   REPLICATE_BASE = "https://api.replicate.com/v1"
   REPLICATE_MUSIC_MODEL_VERSION = os.getenv("REPLICATE_MODEL_VERSION", "")

   AIML_API_KEY = os.getenv("AIML_API_KEY", "")
   AIMLAPI_BASE = "https://api.aimlapi.com/v2/generate/audio"

   DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", HF_MUSIC_MODEL)

   POLL_TIMEOUT_SECONDS = 300
   POLL_INTERVAL_SECONDS = 5

   AUDIO_CACHE_DIR = os.getenv("AUDIO_CACHE_DIR", "/tmp/suno_audio")
   os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)


   # ============================================================
   # PROVIDER: HUGGING FACE (100% GRATIS)
   # ============================================================
   def _hf_headers():
       if not HF_API_KEY:
           raise RuntimeError("HF_API_KEY nao configurada.")
       return {
           "Authorization": "Bearer " + HF_API_KEY,
           "Content-Type": "application/json",
       }


   def _hf_create(prompt, lyrics, instrumental, model):
       payload = {
           "inputs": prompt,
           "parameters": {
               "max_new_tokens": 256,
               "guidance_scale": 3.0,
               "temperature": 1.0,
           },
       }
       log.info("[HF] Gerando musica no MusicGen...")
       resp = requests.post(
           f"{HF_BASE}/{model}",
           json=payload,
           headers=_hf_headers(),
           timeout=180,
       )
       if resp.status_code == 401:
           raise RuntimeError("HF: token invalido. Verifique HF_API_KEY no Render.")
       if resp.status_code == 403:
           raise RuntimeError("HF: acesso negado. Verifique o token.")
       if resp.status_code == 429:
           raise RuntimeError("HF: rate limit. Aguarde 1-2 min e tente de novo.")
       if resp.status_code == 503:
           try:
               err = resp.json()
               wait = err.get("estimated_time", 20)
               raise RuntimeError(f"HF: modelo carregando. Tente em ~{wait:.0f}s.")
           except (ValueError, KeyError):
               raise RuntimeError("HF: modelo carregando, tente em ~30s.")
       if resp.status_code >= 400:
           raise RuntimeError(f"HF erro {resp.status_code}: {resp.text[:300]}")

       audio_bytes = resp.content
       if len(audio_bytes) < 1000:
           raise RuntimeError(f"HF retornou audio muito pequeno ({len(audio_bytes)} bytes).")

       audio_id = f"hf_{int(time.time() * 1000)}"
       cache_path = os.path.join(AUDIO_CACHE_DIR, f"{audio_id}.mp3")
       with open(cache_path, "wb") as f:
           f.write(audio_bytes)
       log.info("[HF] Audio gerado: %s (%.1f KB)", audio_id, len(audio_bytes) / 1024)
       return {"id": audio_id, "status": "completed", "audio_file_path": cache_path, "audio_size": len(audio_bytes)}


   def _hf_status(audio_id):
       cache_path = os.path.join(AUDIO_CACHE_DIR, f"{audio_id}.mp3")
       if os.path.exists(cache_path):
           return {"status": "completed", "audio_file": {"url": f"/api/audio/{audio_id}.mp3", "size":
 os.path.getsize(cache_path)}}
       return {"status": "error", "error": {"message": f"Arquivo {audio_id} nao encontrado."}}


   # ============================================================
   # PROVIDER: REPLICATE (fallback opcional)
   # ============================================================
   def _replicate_headers():
       if not REPLICATE_API_KEY:
           raise RuntimeError("REPLICATE_API_KEY nao configurada.")
       return {"Authorization": "Token " + REPLICATE_API_KEY, "Content-Type": "application/json"}


   def _replicate_create(prompt, lyrics, instrumental, model):
       if not REPLICATE_MUSIC_MODEL_VERSION:
           raise RuntimeError("REPLICATE_MODEL_VERSION nao configurada.")
       payload = {"version": REPLICATE_MUSIC_MODEL_VERSION, "input": {"prompt": prompt, "lyrics": lyrics if not
 instrumental else "", "instrumental": instrumental, "output_format": "mp3"}}
       resp = requests.post(f"{REPLICATE_BASE}/predictions", json=payload, headers=_replicate_headers(), timeout=60)
       if resp.status_code >= 400:
           raise RuntimeError(f"Replicate erro {resp.status_code}: {resp.text[:300]}")
       return resp.json()


   def _replicate_status(prediction_id):
       resp = requests.get(f"{REPLICATE_BASE}/predictions/{prediction_id}", headers=_replicate_headers(), timeout=30)
       if resp.status_code >= 400:
           raise RuntimeError(f"Replicate poll erro {resp.status_code}")
       return resp.json()


   # ============================================================
   # PROVIDER: AIMLAPI (legado)
   # ============================================================
   def _aimlapi_headers():
       if not AIML_API_KEY:
           raise RuntimeError("AIML_API_KEY nao configurada.")
       return {"Authorization": "Bearer " + AIML_API_KEY, "Content-Type": "application/json"}


   def _aimlapi_create(prompt, lyrics, instrumental, model):
       payload = {"model": model, "prompt": prompt, "lyrics": lyrics, "audio_setting": {"audio_sample_rate": 44100,
 "bitrate": 256000, "format": "mp3"}}
       resp = requests.post(AIMLAPI_BASE, json=payload, headers=_aimlapi_headers(), timeout=60)
       if resp.status_code >= 400:
           raise RuntimeError(f"AIMLAPI erro {resp.status_code}: {resp.text[:300]}")
       return resp.json()


   def _aimlapi_status(task_id):
       resp = requests.get(AIMLAPI_BASE, params={"generation_id": task_id}, headers=_aimlapi_headers(), timeout=30)
       if resp.status_code >= 400:
           raise RuntimeError(f"AIMLAPI poll erro {resp.status_code}")
       return resp.json()


   # ============================================================
   # ROTAS
   # ============================================================
   def _default_lyrics_for_instrumental():
       return "[Instrumental]\n[Verse]\n[Outro]\n"


   @app.route("/", methods=["GET"])
   def index():
       try:
           return send_from_directory(".", "index.html")
       except Exception as e:
           return jsonify({"error": str(e)}), 500


   @app.route("/health", methods=["GET"])
   def health():
       return jsonify({"status": "healthy", "provider": MUSIC_PROVIDER, "model": DEFAULT_MODEL}), 200


   @app.route("/api/providers", methods=["GET"])
   def list_providers():
       return jsonify({"active": MUSIC_PROVIDER, "available": {"huggingface": bool(HF_API_KEY), "replicate":
 bool(REPLICATE_API_KEY), "aimlapi": bool(AIML_API_KEY)}, "default_model": DEFAULT_MODEL})


   @app.route("/api/audio/<path:filename>", methods=["GET"])
   def serve_audio(filename):
       return send_from_directory(AUDIO_CACHE_DIR, filename)


   @app.route("/api/generate-music", methods=["POST"])
   def generate_music():
       try:
           data = request.get_json(silent=True) or {}
           prompt = (data.get("prompt") or "").strip()
           lyrics = (data.get("lyrics") or "").strip()
           instrumental = bool(data.get("instrumental", False))
           model = data.get("model") or DEFAULT_MODEL
           provider = (data.get("provider") or MUSIC_PROVIDER).lower()

           if not prompt:
               return jsonify({"error": "O campo prompt e obrigatorio.", "hint": "Descreva o estilo. Ex: 'Lo-fi hip hop
 relaxante com piano'"}), 400
           if len(prompt) < 10:
               return jsonify({"error": "Prompt precisa ter pelo menos 10 caracteres."}), 400
           if len(prompt) > 500:
               return jsonify({"error": "Prompt nao pode ter mais que 500 caracteres."}), 400

           if lyrics and not instrumental:
               log.info("Letra ignorada no MusicGen (so funciona com providers pagos).")

           log.info("[%s] prompt_len=%d instrumental=%s", provider, len(prompt), instrumental)

           if provider == "huggingface":
               if not HF_API_KEY:
                   return jsonify({"error": "HF_API_KEY nao configurada.", "how_to_fix": "Pegue token gratis em
 huggingface.co/settings/tokens e adicione no Render."}), 500
               body = _hf_create(prompt, lyrics, instrumental, model)
               return jsonify({"id": body["id"], "status": "completed", "audio_url": f"/api/audio/{body['id']}.mp3",
 "audio_size_bytes": body.get("audio_size"), "provider": provider, "model": model}), 200

           elif provider == "replicate":
               if not REPLICATE_API_KEY:
                   return jsonify({"error": "REPLICATE_API_KEY nao configurada."}), 500
               body = _replicate_create(prompt, lyrics, instrumental, model)
               return jsonify({"id": body.get("id"), "status": body.get("status", "starting"), "model": model,
 "provider": provider}), 200

           elif provider == "aimlapi":
               if not AIML_API_KEY:
                   return jsonify({"error": "AIML_API_KEY nao configurada."}), 500
               body = _aimlapi_create(prompt, lyrics, instrumental, model)
               return jsonify({"id": body.get("id"), "status": body.get("status", "queued"), "model": model,
 "provider": provider}), 200

           else:
               return jsonify({"error": f"Provider '{provider}' desconhecido.", "valid": ["huggingface", "replicate",
 "aimlapi"]}), 400

       except RuntimeError as e:
           log.exception("Erro de runtime")
           return jsonify({"error": str(e)}), 500
       except requests.RequestException as e:
           log.exception("Erro de rede")
           return jsonify({"error": "Falha de comunicacao.", "details": str(e)}), 502
       except Exception as e:
           log.exception("Erro inesperado")
           return jsonify({"error": "Erro interno.", "details": str(e)}), 500


   @app.route("/api/music-status/<task_id>", methods=["GET"])
   def music_status(task_id):
       try:
           if not task_id:
               return jsonify({"error": "task_id e obrigatorio."}), 400

           if task_id.startswith("hf_"):
               provider = "huggingface"
           elif len(task_id) == 64:
               provider = "replicate"
           else:
               provider = MUSIC_PROVIDER

           start = time.time()
           while True:
               elapsed = time.time() - start
               if elapsed > POLL_TIMEOUT_SECONDS:
                   return jsonify({"id": task_id, "status": "timeout", "error": f"Nao completou em
 {POLL_TIMEOUT_SECONDS}s."}), 504

               log.info("[%s] Poll %s (%.1fs)", provider, task_id, elapsed)

               if provider == "huggingface":
                   body = _hf_status(task_id)
                   if body.get("status") == "completed":
                       return jsonify({"id": task_id, "status": "completed", "audio_url": body["audio_file"]["url"],
 "provider": provider}), 200
                   return jsonify({"id": task_id, "status": "error", "error": body.get("error", {}).get("message",
 "Erro")}), 502

               elif provider == "replicate":
                   body = _replicate_status(task_id)
                   status = body.get("status")
                   if status == "succeeded":
                       output = body.get("output")
                       audio_url = output[0] if isinstance(output, list) else output
                       return jsonify({"id": task_id, "status": "completed", "audio_url": audio_url, "provider":
 provider}), 200
                   if status in ("failed", "canceled"):
                       return jsonify({"id": task_id, "status": "error", "error": str(body.get("error", "Falha"))}),
 502

               else:
                   body = _aimlapi_status(task_id)
                   status = body.get("status")
                   if status == "completed":
                       audio = body.get("audio_file") or {}
                       extra = body.get("extra_info") or {}
                       return jsonify({"id": task_id, "status": "completed", "audio_url": audio.get("url"), "provider":
 provider, "duration_ms": extra.get("music_duration")}), 200
                   if status == "error":
                       err = body.get("error") or {}
                       return jsonify({"id": task_id, "status": "error", "error": err.get("message", "Erro")}), 502

               time.sleep(POLL_INTERVAL_SECONDS)

       except RuntimeError as e:
           return jsonify({"error": str(e)}), 500
       except requests.RequestException as e:
           return jsonify({"error": "Falha de comunicacao.", "details": str(e)}), 502
       except Exception as e:
           log.exception("Erro inesperado")
           return jsonify({"error": "Erro interno.", "details": str(e)}), 500


   if __name__ == "__main__":
       port = int(os.environ.get("PORT", 5000))
       log.info("Suno Studio | provider=%s | porta=%d", MUSIC_PROVIDER, port)
       app.run(host="0.0.0.0", port=port, debug=False)
 ```
