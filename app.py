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

@app.route('/escuchar', methods=['GET'])
def escuchar():
    id_video = request.args.get('id')
    
    # Arregla el error de "Incomplete YouTube ID None"
    if not id_video or id_video == "None":
        return jsonify({"error": "ID de video no válido o ausente"}), 400

    url_yt = f"https://www.youtube.com/watch?v={id_video}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        # OPCIONES ANTIBOT ACTUALIZADAS
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android'], # Clientes móviles suelen tener menos bloqueos
                'player_skip': ['webpage', 'configs'],
            }
        },
        # Forzamos una cabecera de navegador real
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_yt, download=False)
            # Redirigimos al flujo de audio real
            return redirect(info['url'])
    except Exception as e:
        print(f"Error detectado: {str(e)}")
        # Si falla, devolvemos el error para verlo en el Log de Zeabur
        return jsonify({"error": "YouTube bloqueó la petición. Intenta con otra canción o usa cookies."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
