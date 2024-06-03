import os
import requests
from github import Github

# Token de acceso a la API de GitHub
TOKEN = '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'

def autenticar():
    return Github(TOKEN)

def clonar_repo(repo_url, dest_path):
    os.system(f'git clone {repo_url} {dest_path}')

def modificar_archivo(archivo, contenido):
    with open(archivo, 'w') as file:
        file.write(contenido)

def subir_archivo(repo, archivo, mensaje_commit):
    with open(archivo, 'r') as file:
        contenido = file.read()
        repo.create_file(archivo, mensaje_commit, contenido)

def obtener_ultimos_cambios(github_instance, num_cambios=5):
    user = github_instance.get_user()
    repos = user.get_repos()
    commits = []
    
    for repo in repos:
        try:
            repo_commits = repo.get_commits()
            for commit in repo_commits:
                commits.append({
                    "repo_name": repo.name,
                    "author": commit.commit.author.name,
                    "date": commit.commit.author.date,
                    "message": commit.commit.message,
                    "files": commit.files
                })
        except Exception as e:
            print(f'Error al obtener los commits del repositorio "{repo.name}": {e}')

    # Ordenar commits por fecha
    commits.sort(key=lambda x: x["date"], reverse=True)

    # Mostrar los últimos num_cambios commits
    for i, commit in enumerate(commits[:num_cambios]):
        print(f'\nCambio #{i+1}:')
        print(f'Repositorio: {commit["repo_name"]}')
        print(f'Autor: {commit["author"]}')
        print(f'Fecha: {commit["date"]}')
        print(f'Mensaje: {commit["message"]}')
        for file in commit["files"]:
            print(f'  Archivo: {file.filename}')
            print(f'  Cambios: {file.changes}')
            print(f'  Estado: {file.status}')

def listar_repositorios(github_instance):
    repos = github_instance.get_user().get_repos()
    for repo in repos:
        print(repo.name)

def listar_archivos(repo):
    contents = repo.get_contents('')
    for content in contents:
        print(content.path)

def menu_interactivo(github_instance):
    while True:
        print("\n--- MENÚ INTERACTIVO ---")
        print("1. Clonar repositorio")
        print("2. Modificar archivo")
        print("3. Subir archivo")
        print("4. Ver historial de cambios")
        print("5. Listar repositorios")
        print("6. Listar archivos de un repositorio")
        print("0. Salir")
        opcion = input("Elige una opción: ")

        if opcion == '1':
            repo_url = input("Ingresa la URL del repositorio a clonar: ")
            dest_path = input("Ingresa la ruta de destino para clonar el repositorio: ")
            clonar_repo(repo_url, dest_path)
        elif opcion == '2':
            archivo = input("Ingresa el nombre del archivo a modificar: ")
            contenido = input("Ingresa el nuevo contenido del archivo: ")
            modificar_archivo(archivo, contenido)
        elif opcion == '3':
            repo_nombre = input("Ingresa el nombre del repositorio donde subir el archivo: ")
            repo = github_instance.get_user().get_repo(repo_nombre)
            archivo = input("Ingresa el nombre del archivo a subir: ")
            mensaje_commit = input("Ingresa el mensaje del commit: ")
            subir_archivo(repo, archivo, mensaje_commit)
        elif opcion == '4':
            obtener_ultimos_cambios(github_instance)
        elif opcion == '5':
            listar_repositorios(github_instance)
        elif opcion == '6':
            repo_nombre = input("Ingresa el nombre del repositorio para listar archivos: ")
            repo = github_instance.get_user().get_repo(repo_nombre)
            listar_archivos(repo)
        elif opcion == '0':
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, elige una opción del menú.")

# Autenticación
github = autenticar()
if github:
    menu_interactivo(github)
else:
    print("No se pudo autenticar en GitHub. Revisa tu token de acceso.")

