import json
import socket
import serial
import requests
from django.conf import settings
from apps.kiosk.pos_pasargad_client import PosPasargadClient

class POSService:
    """سرویس مدیریت ارتباط با دستگاه‌های کارتخوان (POS)"""
    
    @classmethod
    def send_via_bridge(cls, pos_device, amount):
        """ارسال مبلغ از طریق سرویس Bridge محلی (HTTP)."""
        bridge_url = getattr(settings, 'POS_BRIDGE_URL', '')
        if not bridge_url:
            return False, 'POS_BRIDGE_URL تنظیم نشده است.'
        url = bridge_url.rstrip('/') + '/pay'
        payload = {
            'amount': int(amount),
            'bank': pos_device.bank,
            'device_type': pos_device.device_type,
            'terminal_id': pos_device.terminal_id,
            'merchant_id': pos_device.merchant_id,
            'connection_type': pos_device.connection_type,
            'ip_address': pos_device.ip_address,
            'port': pos_device.port,
            'serial_port': pos_device.serial_port,
            'baud_rate': pos_device.baud_rate,
        }
        try:
            resp = requests.post(url, json=payload, timeout=15)
            data = resp.json() if resp.headers.get('content-type','').startswith('application/json') else {}
            if resp.ok and isinstance(data, dict) and data.get('ok'):
                return True, ''
            msg = data.get('message') if isinstance(data, dict) else resp.text
            return False, msg or 'Bridge error'
        except requests.RequestException as e:
            return False, f'Bridge connection error: {e}'

    @classmethod
    def send_to_pos_tcp(cls, pos_device, amount):
        """ارسال مبلغ به دستگاه پوز از طریق TCP/IP"""
        if pos_device.bank == 'PASARGAD':
            # بررسی استفاده از Bridge
            if getattr(settings, 'POS_BRIDGE_URL', '') and not getattr(settings, 'POS_TEST_MODE', True):
                return cls.send_via_bridge(pos_device, amount)
            
            # استفاده از کلاینت پاسارگاد
            if getattr(settings, 'POS_TEST_MODE', True):
                return True, ''
            
            ip = pos_device.ip_address
            port = pos_device.port
            if not ip or not port:
                return False, 'IP/Port دستگاه پوز تنظیم نشده است.'
            
            try:
                client = PosPasargadClient(ip=str(ip), port=int(port), timeout_ms=30000)
                pos_res = client.sale_toman(int(amount))
                result = bool(pos_res.get('ok'))
                if result:
                    return True, ''
                else:
                    msg = pos_res.get('message_fa') or pos_res.get('error_name') or 'خطای نامشخص'
                    return False, msg
            except Exception as e:
                return False, str(e)
            
        elif pos_device.device_type == 'VERIFONE_VX520' and pos_device.bank == 'SAMAN':
            try:
                data = {
                    'amount': amount,
                    'terminal_id': pos_device.terminal_id,
                    'merchant_id': pos_device.merchant_id
                }
                json_data = json.dumps(data)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((pos_device.ip_address, pos_device.port))
                sock.sendall(json_data.encode())
                response = sock.recv(1024).decode()
                sock.close()
                if 'success' in response.lower():
                    return True, ''
                else:
                    return False, response
            except socket.error as e:
                return False, f"خطای اتصال: {str(e)}"
            except Exception as e:
                return False, f"خطای ارتباط با دستگاه پوز: {str(e)}"
        
        return False, "این مدل دستگاه پوز یا بانک در حال حاضر از طریق TCP پشتیبانی نمی‌شود."

    @classmethod
    def send_to_pos_serial(cls, pos_device, amount):
        """ارسال مبلغ به دستگاه پوز از طریق پورت سریال"""
        if pos_device.bank == 'PASARGAD' and getattr(settings, 'POS_BRIDGE_URL', '') and not getattr(settings, 'POS_TEST_MODE', True):
            return cls.send_via_bridge(pos_device, amount)
            
        if pos_device.device_type == 'VERIFONE_VX520' and pos_device.bank == 'SAMAN':
            try:
                command = f"AMOUNT:{amount};TERMINAL:{pos_device.terminal_id};MERCHANT:{pos_device.merchant_id}\r\n"
                ser = serial.Serial(
                    port=pos_device.serial_port,
                    baudrate=pos_device.baud_rate,
                    timeout=10
                )
                ser.write(command.encode())
                response = ser.readline().decode().strip()
                ser.close()
                if response.startswith('OK'):
                    return True, ''
                else:
                    return False, response
            except serial.SerialException as e:
                return False, f"خطای پورت سریال: {str(e)}"
            except Exception as e:
                return False, f"خطای ارتباط با دستگاه پوز: {str(e)}"
        
        return False, "این مدل دستگاه پوز یا بانک در حال حاضر از طریق سریال پشتیبانی نمی‌شود."
