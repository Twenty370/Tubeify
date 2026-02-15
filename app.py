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

@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q')
    # Cambiamos 'ytsearch' por 'ytmsearch' para buscar solo en YouTube Music
    ydl_opts = {
        'quiet': True, 
        'noplaylist': True, 
        'extract_flat': True,
        'cookiefile': 'cookies.txt' # Usar cookies ayuda a obtener mejores resultados
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # 'ytmsearch10' limita la búsqueda a los 10 mejores resultados de Music
        info = ydl.extract_info(f"ytmsearch10:{query}", download=False)
        resultados = [{"id": e['id'], "titulo": e['title']} for e in info['entries']]
        return jsonify(resultados)

@app.route('/escuchar', methods=['GET'])
def escuchar():
    id_video = request.args.get('id')
    if not id_video or id_video == "None":
        return jsonify({"error": "ID no válido"}), 400

    # Forzamos la URL de YouTube Music
    url_yt = f"https://music.youtube.com/watch?v={id_video}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'cookiefile': 'cookies.txt', # Crítico para evitar el error "Sign in to confirm you're not a bot"
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'],
                'player_skip': ['webpage', 'configs'],
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_yt, download=False)
            return redirect(info['url'])
    except Exception as e:
        return jsonify({"error": f"Error en Music: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
