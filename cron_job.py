import subprocess
import sys
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from crontab import CronTab
import logging
import shutil
import os

# Configuración del Logger
def configure_logger():
    log_directory = "/opt/log"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logging.basicConfig(
        filename=os.path.join(log_directory, "cron_programmer.log"),
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s",
    )

# Función para enviar notificaciones
def send_notification(message, status):
    logging.info(f"Enviando notificación: {message} - {status}")
    subprocess.run(["/opt/admin/telegram_notifications.sh", message, status])

# Configuración del cliente de Google Sheets
def get_google_sheets_client(cred_path, scopes):
    logging.info("Configurando el cliente de Google Sheets.")
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scopes)
    return gspread.authorize(creds)

# Obtener datos de la hoja de cálculo de Google Sheets
def get_data_from_sheet(client, spreadsheet_id):
    logging.info("Obteniendo datos de la hoja de cálculo.")
    sheet = client.open_by_key(spreadsheet_id).sheet1
    return sheet.get_all_records()

# Crear una tarea en el crontab
def create_cron_job(command, schedule, comment=None):
    logging.info(f"Creando tarea en crontab: {command} - {schedule}")
    cron = CronTab(user=True)
    job = cron.new(command=command, comment=comment)
    job.setall(schedule)
    cron.write()
    return job

# Eliminar todas las tareas del crontab
def remove_all_cron_jobs():
    logging.info("Eliminando todas las tareas del crontab.")
    cron = CronTab(user=True)
    cron.remove_all()
    cron.write()

# Hacer una copia de seguridad del crontab actual
def backup_crontab(filename):
    logging.info(f"Realizando copia de seguridad del crontab en {filename}.")
    cron = CronTab(user=True)
    with open(filename, "w") as f:
        for job in cron:
            f.write(str(job))
            f.write("\n")

# Mapeo de periodicidad a programación crontab
def map_periodicity_to_cron(periodicity, hour):
    logging.info(f"Mapeando periodicidad: {periodicity} a crontab con hora: {hour}.")
    hour, minute = map(int, hour.split(":"))
    periodicity_map = {
        "diario": f"{minute} {hour} * * *",
        "semana laboral": f"{minute} {hour} * * 1-5",
        "semanal": f"{minute} {hour} * * 0",
        "mensual": f"{minute} {hour} 1 * *",
        "trimestral": f"{minute} {hour} 1 */3 *",
        "cuatrimestral": f"{minute} {hour} 1 */4 *",
        "semestral": f"{minute} {hour} 1 */6 *",
        "anual": f"{minute} {hour} 1 1 *"
    }
    return periodicity_map.get(periodicity, None)

# Mapeo de la ejecución del script al comando crontab
def map_exec_to_cron(id, language, script, route_script, output):
    logging.info(f"Mapeando ejecución de script: {script} para crontab.")
    executable = f"python3 {route_script}" if language == "python" else f"{route_script}"
    command = (
        "{ "
        + f"""/opt/admin/telegram_notifications.sh "{id}({route_script})" Starting && """
        + f"{executable} > /opt/output/{output} && "
        + f"""/opt/admin/telegram_notifications.sh "{id}({route_script})" Finished ;"""
        + " } || "
        + f"""/opt/admin/telegram_notifications.sh "{id}({route_script})" Error"""
    )
    return command

# Preparar el directorio para scripts
def prepare_directory(directory):
    logging.info(f"Preparando directorio: {directory}.")
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

# Subir archivos a Google Drive y limpiar el directorio
def upload_and_cleanup(directory, gdrive_folder):
    logging.info(f"Subiendo archivos del directorio: {directory} a Google Drive y limpiando.")
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            subprocess.run(["python3", "/opt/admin/drive_uploader_downloader.py", "subir", gdrive_folder, filepath])
            os.remove(filepath)
            logging.info(f"Archivo subido y eliminado: {filename}")

def main():
    # Configuración inicial del logger
    configure_logger()
    send_notification("cron_job.py", "Starting")

    # Verifica que el archivo de credenciales existe
    cred_path = "/opt/admin/credentials.json"
    if not os.path.exists(cred_path):
        logging.error("El archivo de credenciales no existe.")
        send_notification("El archivo de credenciales no existe.", "Error")
        exit(1)

    scopes_sheets = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    try:
        # Obtener cliente de Google Sheets
        client_sheets = get_google_sheets_client(cred_path, scopes_sheets)
        data = get_data_from_sheet(client_sheets, "AQUI_VA_TU_ID_DE_GOOGLE_SHEET")
        logging.info("Datos leídos desde Google Sheets correctamente.")

        # Filtrar datos activos
        filtered_data = []
        for row in data:
            if row["ACTIVA"].upper() == "TRUE":
                if not all(row.values()):
                    identificador = row["IDENTIFICADOR"]
                    mensagge = f"El identificador {identificador} no puede ser programado por falta de información."
                    logging.error(mensagge)
                    send_notification(mensagge, "Error")
                    continue
                filtered_data.append(row)
        logging.info(f"Filtrado completado. Total filas activas: {len(filtered_data)}")

        # Configurar el directorio de scripts
        directorio = "/opt/program_script_drive/"
        prepare_directory(directorio)

        # Backup y limpieza de crontab
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        backup_crontab(f"/opt/log/crontab_copia_{fecha_actual}.txt")
        remove_all_cron_jobs()

        # Programar este propio script
        cron_schedule = "0 3 * * *"
        program = "python3 /opt/admin/cron_programmer.py"
        create_cron_job(program, cron_schedule, comment="cron_programmer")

        # Procesar cada fila de datos filtrados
        for row in filtered_data:
            identificador = row["IDENTIFICADOR"]
            script = row["NOMBRE_SCRIPT"]
            ruta_script = f"/opt/program_script_drive/{script}"
            lenguaje = row["LENGUAJE"].lower()
            output = row["NOMBRE_SALIDA"].lower()
            periodicidad = row["PERIOCIDAD"].lower()
            hora = row["HORA"]

            # Descargar y mover el script desde Google Drive
            logging.info(f"Descargando y moviendo script: {script}")
            subprocess.run(["python3", "/opt/admin/drive_uploader_downloader.py", "descargar", "Scrips_download", script])
            subprocess.run(["mv", script, "/opt/program_script_drive/"])

            # Definir el comando del script
            program = map_exec_to_cron(identificador, lenguaje, script, ruta_script, output)

            try:
                cron_schedule = map_periodicity_to_cron(periodicidad, hora)
                if cron_schedule is None:
                    raise ValueError(f"Periodicidad desconocida: {periodicidad}")

                # Añadir la tarea al crontab con el identificador como comentario
                create_cron_job(program, cron_schedule, comment=identificador)
                logging.info(f"Tarea añadida al crontab:\n{identificador}\n{cron_schedule} {ruta_script}")

            except ValueError as e:
                mensagge = f"Error al procesar la periodicidad para el identificador {row['IDENTIFICADOR']}: {str(e)}"
                logging.error(mensagge)
                send_notification(mensagge, "Error")
                continue

        # Subir y limpiar los archivos de salida
        upload_and_cleanup("/opt/output/", "Output_scrips")

        logging.info("Programación en crontab completada correctamente.")
        send_notification("cron_programmer.py", "Finished")

    except Exception as e:
        mensagge = f"Error al procesar la hoja de cálculo: {str(e)}"
        logging.error(mensagge)
        send_notification(mensagge, "Error")

if __name__ == "__main__":
    main()
