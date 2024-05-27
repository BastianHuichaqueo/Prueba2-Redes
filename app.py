from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

campus = ["zona core", "campus uno", "campus matriz", "sector outsourcing"]
dispositivos_por_campus = {campus_name: [] for campus_name in campus}

GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "BastianHuichaqueo"
REPO_NAME = "Prueba2-Redes"
ACCESS_TOKEN = "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"

def commit_to_github(file_path, commit_message):
    with open(file_path, "r") as file:
        content = file.read()
    
    encoded_content = content.encode("utf-8").decode("utf-8")
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    headers = {"Authorization": f"token {ACCESS_TOKEN}"}
    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": "main"
    }
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code, response.json()

@app.route('/campus', methods=['GET'])
def get_campus():
    return jsonify(campus)

@app.route('/campus', methods=['POST'])
def add_campus():
    new_campus = request.json.get('name')
    if new_campus and new_campus not in campus:
        campus.append(new_campus)
        dispositivos_por_campus[new_campus] = []
        status, response = commit_to_github("documentacion.md", f"Agregar campus {new_campus}")
        if status == 201:
            return jsonify({"message": "Campus agregado exitosamente."}), 201
        else:
            return jsonify(response), status
    return jsonify({"error": "Nombre de campus inválido o ya existe."}), 400

@app.route('/dispositivo', methods=['POST'])
def add_device():
    campus_name = request.json.get('campus')
    device_name = request.json.get('name')
    if campus_name in campus and device_name:
        dispositivos_por_campus[campus_name].append(device_name)
        status, response = commit_to_github("documentacion.md", f"Agregar dispositivo {device_name} a {campus_name}")
        if status == 201:
            return jsonify({"message": "Dispositivo agregado exitosamente."}), 201
        else:
            return jsonify(response), status
    return jsonify({"error": "Campus o nombre de dispositivo inválido."}), 400

@app.route('/dispositivos', methods=['GET'])
def get_devices():
    return jsonify(dispositivos_por_campus)

@app.route('/dispositivo', methods=['DELETE'])
def delete_device():
    campus_name = request.json.get('campus')
    device_name = request.json.get('name')
    if campus_name in campus and device_name in dispositivos_por_campus[campus_name]:
        dispositivos_por_campus[campus_name].remove(device_name)
        status, response = commit_to_github("documentacion.md", f"Eliminar dispositivo {device_name} de {campus_name}")
        if status == 201:
            return jsonify({"message": "Dispositivo eliminado exitosamente."}), 200
        else:
            return jsonify(response), status
    return jsonify({"error": "Campus o nombre de dispositivo inválido."}), 400

@app.route('/campus', methods=['DELETE'])
def delete_campus():
    campus_name = request.json.get('name')
    if campus_name in campus:
        campus.remove(campus_name)
        del dispositivos_por_campus[campus_name]
        status, response = commit_to_github("documentacion.md", f"Eliminar campus {campus_name}")
        if status == 201:
            return jsonify({"message": "Campus eliminado exitosamente."}), 200
        else:
            return jsonify(response), status
    return jsonify({"error": "Nombre de campus inválido."}), 400

if __name__ == '__main__':
    app.run(debug=True)

