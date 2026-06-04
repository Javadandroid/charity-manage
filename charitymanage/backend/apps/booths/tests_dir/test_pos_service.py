from django.test import TestCase
from unittest.mock import patch, MagicMock
from apps.booths.models import POSDevice, Booth
from apps.events.models import Event
from apps.booths.services.pos_service import send_to_pos_tcp, send_to_pos_serial
from django.test import override_settings

class PosServiceTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name="Test Event",
            start_date="2023-01-01",
            end_date="2023-01-10",
            location="Test Location"
        )
        self.booth = Booth.objects.create(name="Test Booth", event=self.event)

        self.tcp_pos = POSDevice.objects.create(
            booth=self.booth,
            name="TCP POS",
            device_type='VERIFONE_VX520',
            connection_type='TCP',
            bank='SAMAN',
            ip_address="192.168.1.100",
            port=8583,
            terminal_id="12345",
            merchant_id="67890"
        )

        self.serial_pos = POSDevice.objects.create(
            booth=self.booth,
            name="Serial POS",
            device_type='VERIFONE_VX520',
            connection_type='SERIAL',
            bank='SAMAN',
            serial_port="COM1",
            baud_rate=9600,
            terminal_id="12345",
            merchant_id="67890"
        )

    @override_settings(POS_TEST_MODE=False)
    @patch('apps.booths.services.pos_service.socket.socket')
    def test_send_to_pos_tcp_success(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.return_value = b'{"status": "OK"}'

        success, error = send_to_pos_tcp(self.tcp_pos, 1000)

        self.assertTrue(success)
        self.assertEqual(error, "")
        mock_socket.connect.assert_called_with(("192.168.1.100", 8583))
        mock_socket.sendall.assert_called()

    @override_settings(POS_TEST_MODE=False)
    @patch('apps.booths.services.pos_service.serial.Serial')
    def test_send_to_pos_serial_success(self, mock_serial_class):
        mock_serial = MagicMock()
        mock_serial_class.return_value.__enter__.return_value = mock_serial
        mock_serial.readline.return_value = b"OK\r\n"

        success, error = send_to_pos_serial(self.serial_pos, 1000)

        self.assertTrue(success)
        self.assertEqual(error, "")
        mock_serial.write.assert_called()
