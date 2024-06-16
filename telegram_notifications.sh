#!/bin/bash
#
# telegram_notifications.sh
#
# Este script envía notificaciones a través de Telegram usando la API del bot.
#
# Requiere que se haya creado un bot en Telegram y se haya obtenido el token del bot
# así como el chat_id donde se recibirán las notificaciones.
#

# Token de acceso del bot de Telegram
TOKEN="Introduce el token de tu bot"

# ID del chat donde se enviarán las notificaciones
CHAT_ID="Introduce el ID de tu chat"

# Mensaje que se enviará como notificación
MESSAGE="$1"

# Acción del mensaje (opcional)
STATUS="$2"

# Función para enviar el mensaje a través de la API de Telegram
send_telegram_message() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" -d chat_id="$CHAT_ID" -d text="$message" > /dev/null 2>&1
}

# Verificar si el segundo parámetro (STATUS) está vacío
if [ -z "$STATUS" ]; then
    send_telegram_message "$MESSAGE"
    exit 0
fi

# Convertir STATUS a minúsculas
STATUS_LOWER=$(echo "$STATUS" | tr '[:upper:]' '[:lower:]')

# Verificar el estado y enviar el mensaje correspondiente
case "$STATUS_LOWER" in
    "starting")
        MESSAGE="Starting $MESSAGE"
        ;;
    "finished")
        MESSAGE="Finished $MESSAGE"
        ;;
    "error")
        MESSAGE="Error executing $MESSAGE"
        ;;
    *)
        echo "Unknown status: $STATUS"
        exit 1
        ;;
esac

# Enviar el mensaje final
send_telegram_message "$MESSAGE"
