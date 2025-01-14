import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import markdown

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

ARCHIVOS_PATH = 'archivos'
DATASETS_PATH = 'archivos/datasets/'  # Ruta a los datasets

# Servir las imágenes desde la carpeta archivos
@app.route('/archivos/<filename>')
def serve_image(filename):
    return send_from_directory(ARCHIVOS_PATH, filename)

# Función para ejecutar el notebook
def ejecutar_notebook(notebook_path):
    try:
        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)

        # Reemplazar rutas relativas por rutas absolutas en las celdas del notebook
        for cell in nb.cells:
            if cell.cell_type == "code":
                if 'index' in cell.source:
                    if 'archivos/datasets' in cell.source:
                        cell.source = cell.source.replace('archivos/datasets', DATASETS_PATH)

        # Ejecutar el notebook
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': './'}})

        # Generar salida como HTML
        output = "<html><body style='font-family: Arial, sans-serif; font-size: 16px;'>"

        # Iterar sobre las celdas para obtener contenido de markdown y resultados de código
        for cell in nb.cells:
            if cell.cell_type == "code":
                if "outputs" in cell:
                    for output_cell in cell.outputs:
                        if output_cell.output_type == "stream":
                            output += "<pre style='background-color: #f4f4f4; padding: 10px;'>" + ''.join(output_cell.text) + "</pre>"
                        elif output_cell.output_type == "execute_result":
                            output += "<pre style='background-color: #f4f4f4; padding: 10px;'>" + str(output_cell['data']['text/plain']) + "</pre>"
                output += "<br>"
            elif cell.cell_type == "markdown":
                # Convertir markdown a HTML
                html_content = markdown.markdown(cell.source)
                output += f"<div class='markdown' style='font-size: 18px; color: #555; margin-bottom: 20px;'>{html_content}</div>"

        output += "</body></html>"

        return {"status": "success", "output": output}

    except Exception as e:
        return {"status": "error", "output": str(e)}

# Endpoint para ejecutar el notebook
@app.route('/run-notebook', methods=['POST'])
def run_notebook():
    data = request.json
    notebook_name = data['notebook_name']
    notebook_path = os.path.join(ARCHIVOS_PATH, notebook_name)

    if not os.path.exists(notebook_path):
        return jsonify({"status": "error", "output": "El archivo no existe"})

    result = ejecutar_notebook(notebook_path)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
