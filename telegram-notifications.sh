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
TOKEN="6713386715:AAEeWOWQaeordv1Ev2yaCbMPsrD4ULt9C5U"

# ID del chat donde se enviarán las notificaciones
CHAT_ID="1187883983"

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






* * * * * /usr/bin/logger -t CRON "Starting /opt/prueba3.py" && /opt/telegram_notify.sh "Starting /opt/prueba3.py" && python3 /opt/prueba3.py  && /usr/bin/logger -t CRON "Finished /opt/prueba3.py" && /opt/telegram_notify.sh "Finished /opt/prueba3.py"
