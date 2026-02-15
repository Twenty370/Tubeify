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

# Reproducción con cookies para evitar bloqueos de bots
@app.route('/escuchar', methods=['GET'])
def escuchar():
    id_video = request.args.get('id')
    
    # Validamos que el ID no sea nulo para evitar errores de URL truncada
    if not id_video or id_video == "None":
        return jsonify({"error": "ID de video no válido"}), 400

    url_yt = f"https://music.youtube.com/watch?v={id_video}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'cookiefile': 'cookies.txt', # Esto usa tu sesión de Chrome para saltar el bot
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'], # Simula dispositivos móviles para mayor estabilidad
                'player_skip': ['webpage', 'configs'],
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_yt, download=False)
            # Redirigimos al stream de audio directo que ExoPlayer puede reproducir
            return redirect(info['url'])
    except Exception as e:
        print(f"Error en reproducción: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render y Zeabur asignan el puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'cookiefile': 'cookies.txt',
    'cachedir': False, # ESTO evita que yt-dlp guarde basura en el disco del servidor
    # ... resto de tus opciones
}
