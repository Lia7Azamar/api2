import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import nbformat
from nbconvert import HTMLExporter

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

ARCHIVOS_PATH = 'archivos'

# Servir el contenido de un notebook en formato HTML
@app.route('/ver-notebook/<filename>', methods=['GET'])
def view_notebook(filename):
    try:
        # Ruta completa del archivo del notebook
        notebook_path = os.path.join(ARCHIVOS_PATH, filename)

        # Verificar si el archivo existe
        if not os.path.exists(notebook_path):
            return jsonify({"status": "error", "message": "Archivo no encontrado"}), 404

        # Leer el archivo notebook
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)

        # Convertir el notebook a HTML
        html_exporter = HTMLExporter()
        body, resources = html_exporter.from_notebook_node(nb)

        # Devolver el contenido HTML generado
        return jsonify({"status": "success", "output": body})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
