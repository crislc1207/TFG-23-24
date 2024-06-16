from fastapi import FastAPI, File, UploadFile, HTTPException  # Importa clases y funciones necesarias de FastAPI
from fastapi.responses import Response  # Importa la clase Response de FastAPI para manejar respuestas HTTP
from google.oauth2 import service_account  # Importa el módulo para gestionar las credenciales de servicio de Google
from googleapiclient.discovery import build  # Importa la función para construir un cliente de servicio de Google API
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload  # Importa clases para cargar y descargar archivos desde Google Drive
import io  # Importa el módulo de operaciones de entrada/salida en memoria

app = FastAPI()  # Crea una instancia de la aplicación FastAPI

# Configuración de las credenciales de la API de Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']  # Define los permisos necesarios para acceder a Google Drive
SERVICE_ACCOUNT_FILE = '/opt/admin/credentials.json'  # Ruta al archivo JSON que contiene las credenciales de servicio
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)  # Carga las credenciales desde el archivo JSON
drive_service = build('drive', 'v3', credentials=credentials)  # Crea una instancia del servicio de Google Drive

# Función para encontrar una carpeta por su nombre en Google Drive
def find_folder_by_name(folder_name):
    try:
        results = drive_service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id, name)"
        ).execute()  # Realiza una búsqueda de la carpeta en Google Drive
        folders = results.get('files', [])  # Obtiene la lista de carpetas que coinciden
        if folders:
            return folders[0]  # Devuelve la primera carpeta que coincida
        else:
            return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for folder: {str(e)}")  # Maneja errores HTTP

# Función para subir un archivo a una carpeta específica en Google Drive
def upload_file_to_drive(folder_name, file):
    folder = find_folder_by_name(folder_name)  # Encuentra la carpeta destino en Google Drive
    if folder:
        file_metadata = {
            'name': file.filename,
            'parents': [folder['id']]
        }
        media = MediaIoBaseUpload(file.file, mimetype=file.content_type)  # Crea un objeto para cargar el archivo
        try:
            uploaded_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()  # Sube el archivo al servicio de Google Drive
            return {"file_id": uploaded_file.get('id')}  # Devuelve el ID del archivo subido
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")  # Maneja errores HTTP
    else:
        raise HTTPException(status_code=404, detail=f"Folder '{folder_name}' not found")  # Maneja errores HTTP

# Función para descargar un archivo desde una carpeta específica en Google Drive
def download_file_from_drive(folder_name, file_name):
    folder = find_folder_by_name(folder_name)  # Encuentra la carpeta destino en Google Drive
    if folder:
        try:
            file_list = drive_service.files().list(
                q=f"name='{file_name}' and '{folder['id']}' in parents and trashed=false",
                fields="files(id, name)"
            ).execute().get('files', [])  # Busca el archivo dentro de la carpeta
            if file_list:
                file_id = file_list[0]['id']
                request = drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()  # Descarga el archivo desde Google Drive
                fh.seek(0)
                return fh.read()  # Devuelve el contenido del archivo descargado
            else:
                raise HTTPException(status_code=404, detail=f"File '{file_name}' not found in folder '{folder_name}'")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")  # Maneja errores HTTP
    else:
        raise HTTPException(status_code=404, detail=f"Folder '{folder_name}' not found")  # Maneja errores HTTP

# Función para listar archivos dentro de una carpeta específica en Google Drive
def list_files_in_folder(folder_name):
    folder = find_folder_by_name(folder_name)  # Encuentra la carpeta destino en Google Drive
    if folder:
        try:
            results = drive_service.files().list(
                q=f"'{folder['id']}' in parents and trashed=false",
                fields="files(id, name)"
            ).execute()  # Obtiene la lista de archivos dentro de la carpeta
            files = results.get('files', [])
            return {"files": files}  # Devuelve la lista de archivos
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")  # Maneja errores HTTP
    else:
        raise HTTPException(status_code=404, detail=f"Folder '{folder_name}' not found")  # Maneja errores HTTP

# Endpoint para subir archivos a la carpeta Scrips_download
@app.post("/upload_to_Scrips_download/")
async def upload_to_Scrips_download(file: UploadFile = File(...)):
    return upload_file_to_drive("Scrips_download", file)  # Llama a la función para subir archivo a Google Drive

# Endpoint para descargar archivos de la carpeta Output_scrips
@app.get("/download_from_Output_scrips/")
async def download_from_Output_scrips(file_name: str):
    file_content = download_file_from_drive("Output_scrips", file_name)  # Llama a la función para descargar archivo de Google Drive
    return Response(content=file_content, media_type='application/octet-stream')  # Devuelve el contenido del archivo como respuesta

# Endpoint para listar archivos en la carpeta Output_scrips
@app.get("/list_Output_scrips/")
async def list_Output_scrips_files():
    return list_files_in_folder("Output_scrips")  # Llama a la función para listar archivos en Google Drive
