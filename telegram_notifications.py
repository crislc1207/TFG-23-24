#
# telegram_notifications.py
#
# Este script envía notificaciones a través de Telegram usando la API del bot.
#
# Requiere que se haya creado un bot en Telegram y se haya obtenido el token del bot
# así como el chat_id donde se recibirán las notificaciones.
#

# Importamos el módulo requests, que nos permite enviar solicitudes HTTP
import requests
# Importamos el módulo argparse, que nos permite manejar argumentos de línea de comandos
import argparse

# Definimos una función para enviar mensajes a través de Telegram
def send_telegram_message(api_key, chat_id, mensaje):
    # Construimos la URL de la API de Telegram
    url = f"https://api.telegram.org/bot{api_key}/sendMessage"
    # Definimos los parámetros que se enviarán en la solicitud
    parametros = {
        "chat_id": chat_id,  # El ID del chat al que se enviará el mensaje
        "text": mensaje  # El mensaje que se enviará
    }
    # Enviamos una solicitud POST a la API de Telegram con los parámetros definidos
    response = requests.post(url, json=parametros)
    # Devolvemos la respuesta de la API de Telegram en formato JSON
    return response.json()

# Definimos la función principal que se ejecutará cuando se ejecute el script
def main(mensaje):
    # Definimos el token de nuestro bot de Telegram
    api_key = "Introduce el token de tu bot"
    # Definimos el ID del chat al que queremos enviar mensajes
    chat_id = "Introduce el ID de tu chat"
    # Llamamos a la función para enviar el mensaje
    respuesta = send_telegram_message(api_key, chat_id, mensaje)
    # Verificamos si el mensaje se envió correctamente
    if respuesta['ok']:
        print("Mensaje enviado correctamente.")
    else:
        print("Error al enviar el mensaje:", respuesta['description'])

# Si el script se está ejecutando como el script principal, llamamos a la función principal
if __name__ == "__main__":
    # Creamos un objeto ArgumentParser
    parser = argparse.ArgumentParser(description='Envía un mensaje a través de Telegram.')
    # Añadimos un argumento 'mensaje' al analizador
    parser.add_argument('mensaje', type=str, help='El mensaje que deseas enviar.')
    # Analizamos los argumentos de la línea de comandos
    args = parser.parse_args()
    # Llamamos a la función principal con el mensaje proporcionado como argumento
    main(args.mensaje)
