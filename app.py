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


# Ruta para servir solo las salidas de las celdas de código, incluyendo gráficos
@app.route('/ver-notebook/<filename>', methods=['GET'])
def view_notebook(filename):
    try:
        notebook_path = os.path.join(ARCHIVOS_PATH, filename)

        if not os.path.exists(notebook_path):
            return jsonify({"status": "error", "message": "Archivo no encontrado"}), 404

        # Leer el archivo notebook
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)

        # Extraer las salidas de las celdas de código
        outputs = []
        for cell in nb.cells:
            if cell.cell_type == 'code' and 'outputs' in cell:
                for output in cell.outputs:
                    if 'text' in output:
                        outputs.append({"type": "text", "content": output['text']})
                    elif 'data' in output and 'image/png' in output['data']:
                        outputs.append({"type": "image", "content": output['data']['image/png']})

        return jsonify({"status": "success", "outputs": outputs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
