```python
   
   Suno Studio Backend - gera musica via AIMLAPI.
   Usa o modelo minimax/music-2.0 (a AIMLAPI nao oferece Suno oficial).
   Tambem serve o frontend HTML em /.
   

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

   AIML_API_KEY = os.getenv("AIML_API_KEY")
   if not AIML_API_KEY:
       log.warning("AIML_API_KEY nao definida - adicione no Environment do Render.")

   AIMLAPI_BASE = "https://api.aimlapi.com/v2/generate/audio"

   DEFAULT_MODEL = "minimax/music-2.0"

   POLL_TIMEOUT_SECONDS = 600
   POLL_INTERVAL_SECONDS = 10


   def _aimlapi_headers():
       if not AIML_API_KEY:
           raise RuntimeError("AIML_API_KEY nao configurada no servidor.")
       return {
           "Authorization": "Bearer " + AIML_API_KEY,
           "Content-Type": "application/json",
       }


   def _default_lyrics_for_instrumental():
       return "[Instrumental]\n[Verse]\n[Outro]\n"


   @app.route("/", methods=["GET"])
   def index():
       try:
           return send_from_directory(".", "index.html")
       except Exception as e:
           log.exception("Erro ao servir index.html")
           return jsonify({"error": str(e)}), 500


   @app.route("/health", methods=["GET"])
   def health():
       return jsonify({"status": "healthy"}), 200


   @app.route("/api/generate-music", methods=["POST"])
   def generate_music():
       try:
           data = request.get_json(silent=True) or {}
           prompt = (data.get("prompt") or "").strip()
           lyrics = (data.get("lyrics") or "").strip()
           instrumental = bool(data.get("instrumental", False))
           model = data.get("model") or DEFAULT_MODEL

           if not prompt:
               return jsonify({"error": "O campo prompt e obrigatorio."}), 400
           if len(prompt) < 10:
               return jsonify({"error": "O prompt precisa ter pelo menos 10 caracteres."}), 400
           if len(prompt) > 2000:
               return jsonify({"error": "O prompt nao pode ter mais que 2000 caracteres."}), 400

           if instrumental or not lyrics:
               lyrics = _default_lyrics_for_instrumental()
           elif len(lyrics) > 3000:
               return jsonify({"error": "A letra nao pode ter mais que 3000 caracteres."}), 400

           payload = {
               "model": model,
               "prompt": prompt,
               "lyrics": lyrics,
               "audio_setting": {
                   "audio_sample_rate": 44100,
                   "bitrate": 256000,
                   "format": "mp3",
               },
           }

           log.info("Disparando geracao: model=%s prompt_len=%d", model, len(prompt))
           resp = requests.post(
               AIMLAPI_BASE,
               json=payload,
               headers=_aimlapi_headers(),
               timeout=60,
           )

           if resp.status_code >= 400:
               log.error("AIMLAPI erro %s: %s", resp.status_code, resp.text[:500])
               return jsonify({
                   "error": "AIMLAPI recusou o pedido.",
                   "status_code": resp.status_code,
                   "details": _safe_json(resp),
               }), resp.status_code

           body = resp.json()
           gen_id = body.get("id")
           if not gen_id:
               log.error("AIMLAPI nao retornou id: %s", body)
               return jsonify({"error": "AIMLAPI nao retornou um ID.", "details": body}), 502

           return jsonify({
               "id": gen_id,
               "status": body.get("status", "queued"),
               "model": model,
           }), 200

       except RuntimeError as e:
           log.exception("Configuracao ausente")
           return jsonify({"error": str(e)}), 500
       except requests.RequestException as e:
           log.exception("Erro de rede chamando AIMLAPI")
           return jsonify({"error": "Falha de comunicacao com a AIMLAPI.", "details": str(e)}), 502
       except Exception as e:
           log.exception("Erro inesperado em /api/generate-music")
           return jsonify({"error": "Erro interno do servidor.", "details": str(e)}), 500


   @app.route("/api/music-status/<task_id>", methods=["GET"])
   def music_status(task_id):
       try:
           if not task_id:
               return jsonify({"error": "task_id e obrigatorio."}), 400

           start = time.time()
           while True:
               elapsed = time.time() - start
               if elapsed > POLL_TIMEOUT_SECONDS:
                   log.warning("Timeout (%ds) consultando %s", POLL_TIMEOUT_SECONDS, task_id)
                   return jsonify({
                       "id": task_id,
                       "status": "timeout",
                       "error": "Geracao nao completou em %ds." % POLL_TIMEOUT_SECONDS,
                   }), 504

               log.info("Poll %s (%.1fs)", task_id, elapsed)
               resp = requests.get(
                   AIMLAPI_BASE,
                   params={"generation_id": task_id},
                   headers=_aimlapi_headers(),
                   timeout=30,
               )

               if resp.status_code >= 400:
                   log.error("AIMLAPI erro %s no poll: %s", resp.status_code, resp.text[:500])
                   return jsonify({
                       "error": "AIMLAPI recusou a consulta.",
                       "status_code": resp.status_code,
                       "details": _safe_json(resp),
                   }), resp.status_code

               body = resp.json()
               status = body.get("status")

               if status == "completed":
                   audio = body.get("audio_file") or {}
                   extra = body.get("extra_info") or {}
                   return jsonify({
                       "id": task_id,
                       "status": "completed",
                       "audio_url": audio.get("url"),
                       "content_type": audio.get("content_type"),
                       "file_name": audio.get("file_name"),
                       "file_size": audio.get("file_size"),
                       "duration_ms": extra.get("music_duration"),
                       "sample_rate": extra.get("music_sample_rate"),
                   }), 200

               if status == "error":
                   err = body.get("error") or {}
                   return jsonify({
                       "id": task_id,
                       "status": "error",
                       "error": err.get("message", "Erro desconhecido na geracao."),
                       "details": err,
                   }), 502

               time.sleep(POLL_INTERVAL_SECONDS)

       except RuntimeError as e:
           log.exception("Configuracao ausente")
           return jsonify({"error": str(e)}), 500
       except requests.RequestException as e:
           log.exception("Erro de rede consultando AIMLAPI")
           return jsonify({"error": "Falha de comunicacao com a AIMLAPI.", "details": str(e)}), 502
       except Exception as e:
           log.exception("Erro inesperado em /api/music-status")
           return jsonify({"error": "Erro interno do servidor.", "details": str(e)}), 500


   def _safe_json(resp):
       try:
           return resp.json()
       except ValueError:
           return {"raw": resp.text[:500]}


   if __name__ == "__main__":
       port = int(os.environ.get("PORT", 5000))
       log.info("Iniciando Suno Studio Backend na porta %d", port)
       app.run(host="0.0.0.0", port=port, debug=False)
 ```
