import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Token de acceso del bot de Telegram
TOKEN = "tu_token"

# Configura los alcances (scopes) para Google Sheets
scopes_sheets = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Configuramos las credenciales de Google Sheets API desde el archivo JSON
creds_sheets = ServiceAccountCredentials.from_json_keyfile_name(
    "/opt/credentials.json", scopes_sheets
)

# Autorizamos el cliente de Google Sheets
client_sheets = gspread.authorize(creds_sheets)

# ID de la hoja de cálculo de Google Sheets
spreadsheet_id = "id_de_tu_google_sheet"

# Inicializar el bot con el token de Telegram proporcionado
bot = telebot.TeleBot(TOKEN)

# Crear un teclado personalizado con los comandos disponibles
commands_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
commands_keyboard.add(KeyboardButton("/start"))
commands_keyboard.add(KeyboardButton("/help"))
commands_keyboard.add(KeyboardButton("/list_all"))
commands_keyboard.add(KeyboardButton("/list_active"))


# Función para manejar el comando /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    """
    Gestor de mensajes para el comando /start.

    Envia un mensaje de bienvenida al usuario.

    """
    bot.reply_to(
        message,
        "Bienvenido! Utiliza cualquiera de los comandos disponibles.",
        reply_markup=commands_keyboard,
    )


# Función para manejar el comando /help
@bot.message_handler(commands=["help"])
def help_command(message):
    """
    Gestor de mensajes para el comando /help.

    Envia una ayuda con los comandos disponibles al usuario.

    """
    bot.reply_to(
        message,
        """
        /start - Iniciar el bot
        /help - Mostrar esta ayuda
        /list_all - Listar todas las tareas
        /list_active - Listar todas las tareas activas
        """,
        reply_markup=commands_keyboard
    )


# Función para manejar el comando /list_all
@bot.message_handler(commands=["list_all"])
def list_all(message):
    """
    Gestor de mensajes para el comando /list_all.

    Lista todas las tareas almacenadas en la hoja de cálculo,
    incluyendo las que están activas o desactivadas.

    """
    try:
        # Abrir la hoja de cálculo y obtener todos los registros
        sheet = client_sheets.open_by_key(spreadsheet_id).sheet1
        data = sheet.get_all_records()

        if not data:
            bot.reply_to(message, "No existen registros")
        else:
            # Construir lista de información de programas con identificador no vacío
            programs_info = []
            for row in data:
                if row["IDENTIFICADOR"]:  # Verifica que el identificador no esté vacío
                    status = "Activado" if row["ACTIVA"] == "TRUE" else "Desactivado"
                    program_info = f"{row['IDENTIFICADOR']}: {row['PERIOCIDAD']} a las {row['HORA']} - {status}"
                    programs_info.append(program_info)

            # Construir el mensaje final
            if programs_info:
                reply_message = "\n".join(programs_info)
                bot.reply_to(message, reply_message, reply_markup=commands_keyboard)

    except Exception as e:
        bot.reply_to(
            message,
            f"Error al consultar los registros: {str(e)}",
            reply_markup=commands_keyboard,
        )


# Función para manejar el comando /list_active
@bot.message_handler(commands=["list_active"])
def list_active(message):
    """
    Gestor de mensajes para el comando /list_active.

    Lista solo las tareas activas (ACTIVA='TRUE') almacenadas en la hoja de cálculo.

    """
    try:
        # Abrir la hoja de cálculo y obtener todos los registros
        sheet = client_sheets.open_by_key(spreadsheet_id).sheet1
        data = sheet.get_all_records()

        if not data:
            bot.reply_to(
                message, "No existen registros activos", reply_markup=commands_keyboard
            )
        else:
            # Filtramos por las filas donde 'ACTIVA' es 'TRUE' y validamos los campos
            programs_active = []
            for row in data:
                if row["ACTIVA"] == "TRUE":
                    program_info = f"{row['IDENTIFICADOR']}: {row['PERIOCIDAD']} a las {row['HORA']}"
                    programs_active.append(program_info)

            if programs_active:
                # Construimos el mensaje final con todas las tareas activas
                reply_message = "\n".join(programs_active)
                bot.reply_to(message, reply_message, reply_markup=commands_keyboard)
            else:
                bot.reply_to(message, "No hay filas activas")

    except Exception as e:
        bot.reply_to(message, f"Error al consultar los registros: {str(e)}")


# Función para manejar cualquier otro tipo de mensaje de texto
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """
    Gestor de mensajes para cualquier texto no reconocido como comando.

    Responde con un saludo y muestra los comandos disponibles.
    """
    bot.reply_to(
        message,
        f"Hola, en qué puedo ayudarte? Estos son mis comandos disponibles.",
        reply_markup=commands_keyboard
    )


# Empezar a recibir mensajes
bot.polling()
