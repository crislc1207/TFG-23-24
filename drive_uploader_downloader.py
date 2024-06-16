import os
import argparse
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

def authenticate(credentials_path):
    """
    Autentica con la API de Google Drive usando las credenciales proporcionadas.

    Argumentos:
        credentials_path (str): Ruta al archivo JSON de las credenciales.

    Returns:
        GoogleDrive: Objeto GoogleDrive autenticado.
    """
    gauth = GoogleAuth()
    scope = ['https://www.googleapis.com/auth/drive']
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    return GoogleDrive(gauth)

def find_folder(drive, folder_name):
    """
    Busca una carpeta por su nombre en Google Drive.

    Argumentos:
        drive (GoogleDrive): Objeto GoogleDrive autenticado.
        folder_name (str): Nombre de la carpeta a buscar.

    Returns:
        dict: Carpeta encontrada, o None si no se encuentra.
    """
    folder_list = drive.ListFile({'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder'"}).GetList()
    if folder_list:
        return folder_list[0]  # toma la primera carpeta que coincide
    else:
        return None

def download_file(drive, folder, file_name):
    """
    Busca un archivo por su nombre en una carpeta y lo descarga.

    Argumentos:
        drive (GoogleDrive): Objeto GoogleDrive autenticado.
        folder (dict): Carpeta donde buscar el archivo.
        file_name (str): Nombre del archivo a descargar.
    """
    file_list = drive.ListFile({'q': f"title='{file_name}' and '{folder['id']}' in parents"}).GetList()
    if file_list:
        file1 = file_list[0]  # toma el primer archivo que coincide
        print(f'Descargando archivo: {file1["title"]}')
        file1.GetContentFile(file_name)  # descarga el archivo
    else:
        print(f'Archivo no encontrado: {file_name}')

def upload_file(drive, folder, file_path):
    """
    Sube un archivo a una carpeta en Google Drive.

    Argumentos:
        drive (GoogleDrive): Objeto GoogleDrive autenticado.
        folder (dict): Carpeta donde subir el archivo.
        file_path (str): Ruta al archivo a subir.
    """
    file_name = os.path.basename(file_path)  # Extrae solo el nombre del archivo de la ruta
    file1 = drive.CreateFile({'title': file_name, 'parents': [{'id': folder['id']}]})  # Crea un archivo de GoogleDrive en la carpeta.
    file1.SetContentFile(file_path)  # Establece contenido del archivo
    file1.Upload()  # Sube el archivo.
    print(f'Archivo subido: {file1["title"]}')

def main():
    # Parsea los argumentos de la línea de comandos
    parser = argparse.ArgumentParser(description='Sube o descarga un archivo a Google Drive.')
    parser.add_argument('accion', type=str, help='La acción a realizar: "subir" o "descargar".')
    parser.add_argument('archivo', type=str, help='El nombre del archivo.')
    args = parser.parse_args()

    # Autenticación
    drive = authenticate('/ruta/credentials.json')

    # Busca la carpeta por su nombre
    folder = find_folder(drive, 'Aqui_va_el_nombre_de_tu_carpeta')
    if folder is not None:
        print(f'Carpeta encontrada: {folder["title"]}')
        if args.accion == 'descargar':
            download_file(drive, folder, args.archivo)
        elif args.accion == 'subir':
            upload_file(drive, folder, args.archivo)
        else:
            print('Acción no reconocida. Por favor, especifica "subir" o "descargar".')
    else:
        print('Carpeta no encontrada: TFG')

if __name__ == '__main__':
    main()
