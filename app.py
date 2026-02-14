from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app) # Importante para que tu celular pueda conectarse

@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q')
    ydl_opts = {'quiet': True, 'noplaylist': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch10:{query}", download=False)
        resultados = [{"id": e['id'], "titulo": e['title']} for e in info['entries']]
        return jsonify(resultados)

@app.route('/stream', methods=['GET'])
def stream():
    id_video = request.args.get('id')
    url_yt = f"https://www.youtube.com/watch?v={id_video}"
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url_yt, download=False)
        return jsonify({"url": info['url']})

if __name__ == '__main__':
    # Render asigna un puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
