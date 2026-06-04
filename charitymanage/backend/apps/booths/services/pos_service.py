import socket
import serial
import json
import logging
import requests
from django.conf import settings
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

def send_to_pos_tcp(pos_device, amount):
    """
    Sends payment request to POS over TCP.
    Returns (success_boolean, error_message)
    """
    if getattr(settings, 'POS_TEST_MODE', False):
        return True, ""

    if pos_device.device_type == 'VERIFONE_VX520' and pos_device.bank == 'SAMAN':
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)

            payload = {
                'amount': str(amount),
                'terminal_id': pos_device.terminal_id,
                'merchant_id': pos_device.merchant_id
            }

            sock.connect((pos_device.ip_address, pos_device.port))
            sock.sendall(json.dumps(payload).encode('utf-8'))

            response = sock.recv(1024).decode('utf-8')
            sock.close()

            resp_data = json.loads(response)
            if resp_data.get('status') == 'OK':
                return True, ""
            else:
                return False, resp_data.get('message', _('خطای نامشخص در پوز'))

        except socket.timeout:
            return False, _("خطای تایم اوت در ارتباط با پوز TCP")
        except Exception as e:
            logger.error(f"TCP POS Error: {e}")
            return False, str(e)

    return False, _("نوع دستگاه یا بانک پشتیبانی نمی‌شود")

def send_to_pos_serial(pos_device, amount):
    """
    Sends payment request to POS over Serial.
    Returns (success_boolean, error_message)
    """
    if getattr(settings, 'POS_TEST_MODE', False):
        return True, ""

    if pos_device.device_type == 'VERIFONE_VX520' and pos_device.bank == 'SAMAN':
        try:
            command = f"AMOUNT:{amount};TERMINAL:{pos_device.terminal_id};MERCHANT:{pos_device.merchant_id}\r\n"

            with serial.Serial(
                port=pos_device.serial_port,
                baudrate=pos_device.baud_rate,
                timeout=10
            ) as ser:
                ser.write(command.encode('ascii'))
                response = ser.readline().decode('ascii').strip()

            if response == "OK":
                return True, ""
            else:
                return False, _("پاسخ نامعتبر از پوز سریال")

        except Exception as e:
            logger.error(f"Serial POS Error: {e}")
            return False, str(e)

    return False, _("نوع دستگاه یا بانک پشتیبانی نمی‌شود")

def send_to_pos(pos_device, amount):
    if pos_device.connection_type == 'TCP':
        return send_to_pos_tcp(pos_device, amount)
    elif pos_device.connection_type == 'SERIAL':
        return send_to_pos_serial(pos_device, amount)
    else:
        return False, _("نوع اتصال پشتیبانی نمی‌شود")
