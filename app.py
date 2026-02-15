from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

# Búsqueda optimizada para YouTube Music
@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    # Configuramos yt-dlp para que sea más flexible con los extractores de búsqueda
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'extract_flat': True,
        'cookiefile': 'cookies.txt', # Crítico para evitar bloqueos y obtener resultados reales
        'force_generic_extractor': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Intentamos primero con la búsqueda específica de YouTube Music
            # Si el entorno falla con 'ytmsearch', lo capturamos y usamos 'ytsearch' como respaldo
            try:
                info = ydl.extract_info(f"ytmsearch10:{query}", download=False)
            except Exception:
                info = ydl.extract_info(f"ytsearch10:{query}", download=False)
            
            # Validamos que existan entradas en la respuesta
            if not info or 'entries' not in info:
                return jsonify([])

            resultados = [{"id": e['id'], "titulo": e['title']} for e in info['entries']]
            return jsonify(resultados)
    except Exception as e:
        print(f"Error en búsqueda: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/escuchar', methods=['GET'])
def escuchar():
    id_video = request.args.get('id')
    if not id_video or id_video == "None":
        return jsonify({"error": "ID no válido"}), 400

    url_yt = f"https://music.youtube.com/watch?v={id_video}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'cookiefile': 'cookies.txt',
        'cachedir': False,
        'noplaylist': True,
        # Cambiamos los clientes para evitar el error de PO Token y Cookies
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'mweb', 'tv'], 
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://music.youtube.com',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_yt, download=False)
            return redirect(info['url'])
    except Exception as e:
        print(f"Error en reproducción: {str(e)}")
        return jsonify({"error": "YouTube requiere autenticación adicional. Intenta otra canción."}), 500
