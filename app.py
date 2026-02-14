from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q')
    ydl_opts = {'quiet': True, 'noplaylist': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch10:{query}", download=False)
        resultados = [{"id": e['id'], "titulo": e['title']} for e in info['entries']]
        return jsonify(resultados)

# ESTA ES LA RUTA QUE BUSCA TU APP Y QUE ANTES DABA ERROR 404
@app.route('/escuchar', methods=['GET'])
def escuchar():
    id_video = request.args.get('id')
    url_yt = f"https://www.youtube.com/watch?v={id_video}"
    # Buscamos la URL directa del flujo de audio
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url_yt, download=False)
        url_directa_audio = info['url']
        # Redirigimos a ExoPlayer directamente a la fuente de audio de Google
        return redirect(url_directa_audio)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
