from flask import Flask, render_template, request
import nbformat
from nbconvert import HTMLExporter
import os

# Directorios de los notebooks y las imágenes
notebook_path1 = "/home/emiliano/Escritorio/simulacion/notebooks/3501_Arboles.ipynb"
notebook_path2 = "/home/emiliano/Escritorio/simulacion/notebooks/3501_Fraudes.ipynb"
graph1_path = "static/min.png"
tree_image_path = "static/arbol.png"
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    # Leer y procesar el primer notebook
    with open(notebook_path1, "r", encoding="utf-8") as f:
        notebook_content1 = nbformat.read(f, as_version=4)

    first_dataset_visualization = None  # Visualización de conjuntos de datos
    f1_scores_unscaled = []
    f1_scores_scaled = []

    # Recorrer las celdas del primer notebook y extraer la información necesaria
    for cell in notebook_content1['cells']:
        if cell['cell_type'] == 'code' and 'outputs' in cell:
            for output in cell['outputs']:
                if output['output_type'] in ('display_data', 'execute_result'):  # Visualizaciones
                    if not first_dataset_visualization:
                        first_dataset_visualization = output.data
                if output['output_type'] == 'stream':  # Salidas tipo stream (como print)
                    text = output.get('text', '')
                    if "f1_score WITHOUT preparation" in text:
                        f1_scores_unscaled.append(text.strip())
                    elif "f1_score WITH preparation" in text:
                        f1_scores_scaled.append(text.strip())

    custom_html = """
    <h1>Árboles de Decisión</h1>
    <p>En este caso práctico se pretende resolver un problema de malware en dispositivos android mediante el análisis del tráfico.</p>
    """

    if first_dataset_visualization:
        custom_html += "<h3>Visualización de Conjuntos de Datos</h3>"
        for mime_type, data in first_dataset_visualization.items():
            if mime_type == 'text/html':
                custom_html += f'{data}'

    custom_html += """
    <h3>Resultados del Escalado y Sin Escalado</h3>
    """

    if f1_scores_unscaled or f1_scores_scaled:
        custom_html += "<h3>Puntuaciones de F1</h3><ul>"
        for score in f1_scores_unscaled:
            custom_html += f"<li>Sin Escalado: {score}</li>"
        for score in f1_scores_scaled:
            custom_html += f"<li>Con Escalado: {score}</li>"
        custom_html += "</ul>"

    custom_html += """
    <h3>Límite de Decisión</h3>
    <img src="/{}" alt="Límite de Decisión">
    <h3>Árbol de Decisión</h3>
    <img src="/{}" alt="Árbol de Decisión">
    """.format(graph1_path, tree_image_path)
    
    return render_template("result.html", custom_html=custom_html)

@app.route("/additional", methods=["GET"])
def additional():
    # Leer y procesar el segundo notebook
    with open(notebook_path2, "r", encoding="utf-8") as f:
        notebook_content = f.read()

    notebook_node = nbformat.reads(notebook_content, as_version=4)

    title = ""
    training_section = ""
    for cell in notebook_node.cells:
        if cell["cell_type"] == "markdown" and "Detección de FRAUDES" in cell["source"]:
            title = cell["source"]
        if cell["cell_type"] == "code" and "entrenamiento" in cell["source"].lower():
            training_section = cell["source"]

    # Añadir la sección de entrenamiento del modelo como en la captura proporcionada


    images_html = '''
        <h3>Resultados del Modelo</h3>
        <img src="/static/grafica.png" alt="Gráfica">
        <img src="/static/matriz.png" alt="Matriz de Confusión">
    '''

    # Renderizar el template con las secciones extraídas y las imágenes
    return render_template("notebook_view.html", title=title, images_html=images_html)

if __name__ == "__main__":
    app.run(debug=True)
