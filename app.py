import os
from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
import nbformat
from nbconvert import HTMLExporter

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

ARCHIVOS_PATH = 'archivos'
PAGINA_PATH = 'pagina'  # Ruta a la carpeta donde tienes el HTML y CSS

# Configura Flask para servir archivos estáticos desde la carpeta 'pagina'
app.config['STATIC_FOLDER'] = PAGINA_PATH

# Ruta para servir el archivo HTML desde la carpeta 'pagina'
@app.route('/')
def index():
    return send_from_directory(PAGINA_PATH, 'index.html')

# Ruta para servir el archivo CSS desde la carpeta 'pagina'
@app.route('/pagina/<path:filename>')
def serve_pagina_file(filename):
    return send_from_directory(PAGINA_PATH, filename)

# Ruta para servir el contenido HTML de un notebook
@app.route('/ver-notebook/<filename>', methods=['GET'])
def view_notebook(filename):
    try:
        notebook_path = os.path.join(ARCHIVOS_PATH, filename)
        
        if not os.path.exists(notebook_path):
            return jsonify({"status": "error", "message": "Archivo no encontrado"}), 404

        # Leer el archivo notebook
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)

        # Convertir el notebook a HTML
        html_exporter = HTMLExporter()
        body, resources = html_exporter.from_notebook_node(nb)

        return jsonify({"status": "success", "output": body})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
