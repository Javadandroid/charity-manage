# کلاینت پایتونی ساده برای پروتکل PcPosClassLibrary (پاسارگاد) بدون استفاده از DLL
# منطق از فایل PcPosClassLibrary.txt استخراج شده است.
# ساخت بسته فروش (Sale):
#   هدر 16 بایت:
#     [0..3] طول payload به صورت big-endian
#     [4..5] نوع پروتکل = {0x02, 0xF9}

# نگاشت فارسیِ کامل کدها
ERROR_FA = {
    '000': 'موفق',
    '005': 'لغو',
    '006': 'خطای داخلی سیستم',
    '009': 'سیستم مشغول است',
    '010': 'پرداخت ناقص',
    '012': 'تراکنش نامعتبر',
    '013': 'مبلغ نادرست',
    '014': 'شماره کارت نامعتبر',
    '015': 'پذیرنده نامعتبر',
    '017': 'لغو توسط کاربر',
    '019': 'تراکنش را مجدد وارد کنید',
    '020': 'کد پاسخ نامعتبر',
    '021': 'بدون رویداد',
    '022': 'عملکرد نادرست',
    '025': 'رکورد یافت نشد',
    '030': 'داده موردنیاز نامعتبر',
    '031': 'بانک پذیرنده نامعتبر',
    '032': 'تکمیل جزئی',
    '033': 'کارت منقضی',
    '034': 'تایید نشد',
    '036': 'کارت محدود شده',
    '038': 'تعداد دفعات ورود رمز بیش از حد',
    '039': 'اطلاعات حساب نامشخص',
    '040': 'تراکنش ناشناخته',
    '041': 'کارت مفقودی',
    '043': 'کارت سرقتی',
    '051': 'موجودی ناکافی',
    '054': 'کارت منقضی',
    '055': 'رمز نادرست',
    '056': 'سوابق کارت یافت نشد',
    '057': 'سرویس روی کارت مجاز نیست',
    '058': 'کارت روی پایانه مجاز نیست',
    '061': 'مبلغ برداشت نامعتبر',
    '062': 'کارت محدود شده',
    '064': 'مبلغ برگشت نامعتبر',
    '065': 'شماره برداشت محدود شده',
    '066': 'حساب غیرفعال',
    '067': 'کارت ضبط شود',
    '068': 'پاسخ دیر دریافت شد',
    '075': 'تعداد دفعات رمز عبور بیش از حد',
    '076': 'مبلغ سوئیچ نامعتبر',
    '077': 'روز کاری نامعتبر',
    '078': 'کارت غیرفعال',
    '079': 'حساب تعریف نشده',
    '080': 'خطای داخلی',
    '084': 'بدون پاسخ',
    '085': 'شماره نامعتبر',
    '090': 'عملیات تسویه در حال انجام',
    '091': 'مهلت به پایان رسید (Timeout)',
    '092': 'صادرکننده کارت نامعتبر',
    '093': 'تراکنش ناقص',
    '094': 'پیام تکراری',
    '095': 'رمز قبلی نادرست',
    '096': 'خطای داخلی سوئیچ',
    '097': 'تمام شارژها فروش رفته',
    '098': 'شارژ موجود نیست',
    '099': 'شناسه قبض نادرست',
    '100': 'عملیات چندمرحله‌ای موفق',
    '110': 'کمبود وجه',
    '111': 'مبلغ تراکنش نامعتبر',
    '112': 'خطا در پرداخت',
    '113': 'کاغذ تمام شد',
    '114': 'کاغذ موجود نیست (114)',
    '115': 'لغو (115)',
    '116': 'تایید پرداخت قبض',
    '117': 'سرویس شخص ثالث موجود نیست',
    '118': 'عدم خروج کارت',
    '120': 'مبلغ تراکنش نامعتبر (پایانه)',
    '121': 'رمز پایانه نامعتبر',
    '122': 'شناسه قبض نامعتبر',
    '123': 'شناسه پرداخت نامعتبر',
    '124': 'اطلاعات تراکنش ناکافی',
    '125': 'کد ووچر نامعتبر',
    '126': 'تراکنش یافت نشد',
    '127': 'پایان مهلت کارت‌خوان/رمز',
    '128': 'انصراف کاربر/ترمینال',
    '129': 'خطای دیگر',
    '130': 'کاغذ چاپ موجود نیست',
    '131': 'قیمت نامعتبر',
    '132': 'مهلت به پایان رسید (Timeout)',
    '133': 'قطع ارتباط با پایانه',
    '134': 'حساب چندگانه نامعتبر',
    '135': 'حساب نامعتبر',
    '161': 'مبلغ ناکافی',
    '501': 'خطای MAC',
    '999': 'لغو توسط پایانه',
    '1000': 'سایر',
}
#     [6..7] نوع پیام = {0x45, 0x70}
#   payload برای Sale با پارامترهای حداقلی: "1245" + FS + amount(ریالی) + چهار FS پیاپی (طبق DLL)
#   سپس 20 بایت SHA1 روی (هدر+payload) اضافه می‌شود.
# دریافت پاسخ:
#   خواندن 16 بایت هدر، سپس payloadLen + 20 بایت
#   اعتبارسنجی SHA1 و سپس پارس حداقلی payload بر اساس parsResponse در DLL
# موفقیت وقتی است که TransactionStatus == "000".

import socket
import struct
import hashlib
import sys
import json
import time

FS = 0x1C  # جداکننده فیلدها

# نگاشت کدهای پاسخ به نام‌ها بر اساس enum errorTypes2 در DLL
ERROR_MAP = {
    0: "Approved",
    5: "Cancel2",
    6: "InternalSystemError",
    9: "SystemBusy",
    10: "PartialDispense",
    12: "TransactionInvalid",
    13: "IncorrectAmount",
    14: "InvalidCardNumber",
    15: "InvalidAcquire",
    17: "UserCancel",
    19: "ReenterTransaction",
    20: "InvalidResponseCode",
    21: "NothingHappening",
    22: "IncorrectFunctioning",
    25: "RecordNotFound",
    30: "InvalidRequiredData",
    31: "InvalidAquirer",
    32: "PatialCompletion",
    33: "ExpiredCard33",
    34: "NotApproval",
    36: "RestrictedCard36",
    38: "ExceededPinRetry",
    39: "UnrecognizedAccountInfo",
    40: "UnknownTransaction",
    41: "LostCard",
    43: "StolenCard",
    51: "InsufficientFunds",
    54: "ExpiredCard54",
    55: "IncorrectPIN",
    56: "NoCardRecord",
    57: "ServiceNotAllowedOnCard",
    58: "CardNotAllowedOnTerminal",
    61: "WithdrawalAmount",
    62: "RestrictedCard62",
    64: "InvalidReversalAmount",
    65: "RestrictedWithdrawalNo",
    66: "InactiveAccount",
    67: "CaptureCard",
    68: "ReceivedTooLate",
    75: "ExceededPasswordRetry",
    76: "IncorrectInterchangeAmount",
    77: "InvalidWorkingDay",
    78: "InactiveCard",
    79: "UndefinedAccount",
    80: "InternalError",
    84: "NoResponse",
    85: "InvalidNumber",
    90: "CutoffInProgress",
    91: "TimeOut",
    92: "InvalidCardIssuer",
    93: "IncompleteTransaction",
    94: "DuplicateMessage",
    95: "IncorrectOldPIN",
    96: "InternalSwitchError",
    97: "AllChargeSold",
    98: "ChargeNotAvailable",
    99: "IncorrectBillPaymentID",
    100: "MultistepSuccesful",
    110: "ShortageofFunds",
    111: "InvalidTransactionAmount",
    112: "ErrorInPayment",
    113: "NoPaper",
    114: "NoPaper114",
    115: "Cancel115",
    116: "BillPaymentConfirmation",
    117: "NoThirdParty",
    118: "FailureToWithdrawCard",
    120: "InvalidTransactionAmountTE",
    121: "InvalidTerminalPasswordTE",
    122: "InvalidBillIDTE",
    123: "InvalidPaymentIDTE",
    124: "InsufficientTransactionDataTE",
    125: "InvalideVoucherCodeTE",
    126: "TransactionNotFoundTE",
    127: "CardReaderOrGetPinTimeoutTE",
    128: "TransactionCancelByUserTE",
    129: "OtherErrorTE",
    130: "NoPrintPaperAvailable",
    131: "InvalidPrice",
    132: "Timeout",
    133: "PosDisonnect",
    134: "InvalidMultipleAccount",
    135: "InvalidAccount",
    161: "InsufficientAmount",
    501: "MacFail",
    999: "CancelByPos",
    1000: "Other",
}

def _build_packet_with_s_s2(header_ab: tuple[int,int], header_cd: tuple[int,int], s4: str, s2: str, invoice: str = "", tstr: str = "") -> bytes:
    # buffer کافی بزرگ
    buf = bytearray(2048)
    # هدر نوع/پیام
    buf[4] = header_ab[0]
    buf[5] = header_ab[1]
    buf[6] = header_cd[0]
    buf[7] = header_cd[1]
    # شروع payload از 16
    i = 16
    s = s4.encode('ascii')
    buf[i:i+4] = s; i += 4
    # FS
    buf[i] = FS; i += 1
    # s2 = amount as decimal string
    s2b = s2.encode('ascii')
    buf[i:i+len(s2b)] = s2b; i += len(s2b)
    # چهار FS برای فیلدهای خالی بعد از amount (مطابق DLL: پس از amount چهار 0x1C می‌آید)
    buf[i] = FS; i += 1
    buf[i] = FS; i += 1
    buf[i] = FS; i += 1
    buf[i] = FS; i += 1
    # اگر time داده شود
    if tstr:
        tbytes = tstr.encode('ascii')
        buf[i:i+len(tbytes)] = tbytes; i += len(tbytes)
        # سپس "1234"
        buf[i:i+4] = b"1234"; i += 4
    # اگر invoice برای Sale بدهیم، در انتها ضمیمه می‌شود
    if invoice:
        invb = invoice.encode('ascii')
        buf[i:i+len(invb)] = invb; i += len(invb)
    # طول payload
    payload_len = i - 16
    # نوشتن طول big-endian در 4 بایت اول
    be = struct.pack('>I', payload_len)
    buf[0:4] = be
    # محاسبه SHA1 روی (هدر+payload)
    sha = hashlib.sha1(bytes(buf[0:16+payload_len])).digest()
    buf[16+payload_len:16+payload_len+20] = sha
    packet = bytes(buf[0:16+payload_len+20])
    return packet

# ساخت بسته فروش طبق DLL
def build_sale_packet(amount_rial: int, invoice: str = "", tstr: str = "") -> bytes:
    return _build_packet_with_s_s2((0x02,0xF9),(0x45,0x70), '1245', str(amount_rial), invoice, tstr)

# ساخت بسته Cancel طبق DLL (PCCancel)
def build_cancel_packet(invoice: str = "", tstr: str = "") -> bytes:
    # PCCancel: array={0x0F,0xF8}, array2={0x01,0x70}, s="0000", s2="10"
    return _build_packet_with_s_s2((0x0F,0xF8),(0x01,0x70), '0000', '10', invoice, tstr)

# اعتبارسنجی SHA1
def verify_sha1(frame: bytes) -> bool:
    if len(frame) < 36:
        return False
    calc = hashlib.sha1(frame[:len(frame)-20]).digest()
    mac = frame[-20:]
    return calc == mac

# پارس حداقلی payload بر اساس الگوی parsResponse
# خروجی: دیکشنری از فیلدها
def parse_payload(payload: bytes) -> dict:
    res = {
        'request_code': '', 'txn_status': '', 'amount': '', 'card_mask': '',
        'seq': '', 'date': '', 'rrn': '', 'terminal': '', 'merchant': ''
    }
    try:
        n = len(payload)
        idx = 0
        # request_code (4)
        if idx+4 > n: return res
        res['request_code'] = payload[idx:idx+4].decode('ascii', errors='ignore'); idx += 4
        # txn_status (3)
        if idx+3 > n: return res
        res['txn_status'] = payload[idx:idx+3].decode('ascii', errors='ignore'); idx += 3
        # expect FS
        if idx < n and payload[idx] == FS:
            idx += 1
        else:
            return res
        # amount until FS
        start = idx
        while idx < n and payload[idx] != FS:
            idx += 1
        res['amount'] = payload[start:idx].decode('ascii', errors='ignore')
        if idx < n and payload[idx] == FS:
            idx += 1
        # card mask until FS
        start = idx
        while idx < n and payload[idx] != FS:
            idx += 1
        res['card_mask'] = payload[start:idx].decode('ascii', errors='ignore')
        if idx < n and payload[idx] == FS:
            idx += 1
        # optional seq (4) اگر بلافاصله FS بعدی نبود
        if idx < n and payload[idx] != FS:
            res['seq'] = payload[idx:idx+4].decode('ascii', errors='ignore')
            idx += 4
        # skip FS
        if idx < n and payload[idx] == FS:
            idx += 1
        # date تا FS بعدی
        start = idx
        while idx < n and payload[idx] != FS:
            idx += 1
        res['date'] = payload[start:idx].decode('ascii', errors='ignore')
        if idx < n and payload[idx] == FS:
            idx += 1
        # RRN تا FS بعدی (حداکثر 14)
        start = idx
        while idx < n and payload[idx] != FS:
            idx += 1
        res['rrn'] = payload[start:idx].decode('ascii', errors='ignore').rstrip('\x00')
        if idx < n and payload[idx] == FS:
            idx += 1
        # terminal تا FS بعدی (حداکثر 8، بدون صفرهای ابتدایی)
        start = idx
        while idx < n and payload[idx] != FS:
            idx += 1
        term = payload[start:idx].decode('ascii', errors='ignore').lstrip('0')
        res['terminal'] = term
        if idx < n and payload[idx] == FS:
            idx += 1
        # merchant تا FS بعدی (حداکثر 16)
        start = idx
        while idx < n and payload[idx] != FS:
            idx += 1
        res['merchant'] = payload[start:idx].decode('ascii', errors='ignore')
        if idx < n and payload[idx] == FS:
            idx += 1
        # ادامه فیلدها در فروشِ معمولی معمولاً تمام می‌شود؛ فیلدهای بعدی مربوط به گزارش‌هاست.
    except Exception:
        pass
    return res

# ارسال/دریافت
def transact(ip: str, port: int, amount_rial: int, timeout_ms: int = 20000, debug: bool = False, action: str = 'sale', invoice: str = ""):
    if action == 'sale':
        pkt = build_sale_packet(amount_rial, invoice)
    elif action == 'cancel':
        pkt = build_cancel_packet(invoice)
    else:
        raise ValueError('Unsupported action: ' + action)
    with socket.create_connection((ip, port), timeout=timeout_ms/1000.0) as s:
        s.settimeout(timeout_ms/1000.0)
        s.sendall(pkt)
        if debug:
            print(json.dumps({'debug_send_hex': pkt.hex()}))
        # خواندن هدر
        hdr = b''
        while len(hdr) < 16:
            chunk = s.recv(16 - len(hdr))
            if not chunk:
                break
            hdr += chunk
        if len(hdr) < 16:
            return {'ok': False, 'message': 'no header'}
        # طول payload
        payload_len = struct.unpack('>I', hdr[0:4])[0]
        total_to_read = payload_len + 20
        body = b''
        while len(body) < total_to_read:
            chunk = s.recv(total_to_read - len(body))
            if not chunk:
                break
            body += chunk
        frame = hdr + body
        if debug:
            print(json.dumps({'debug_recv_hex': frame.hex()}))
        if len(body) < total_to_read:
            return {'ok': False, 'message': 'incomplete frame', 'got': len(body), 'need': total_to_read}
        # اعتبارسنجی SHA1
        if not verify_sha1(frame):
            # DLL در صورت عدم تطابق MAC، خطا می‌دهد
            return {'ok': False, 'message': 'sha1 mismatch'}
        # پارس
        payload = frame[16:16+payload_len]
        # هدر [4..7] برای تعیین نوع پاسخ لازم نیست اینجا
        parsed = parse_payload(payload)
        txn = parsed.get('txn_status') or ''
        approved = (txn == '000')
        # نام خطا بر اساس نگاشت
        err_name = None
        try:
            if txn and txn.isdigit():
                err_name = ERROR_MAP.get(int(txn))
        except Exception:
            err_name = None
        # پیام فارسی
        msg_fa = ERROR_FA.get(txn)
        out = {
            'ok': bool(approved),
            'message': 'Success' if approved else 'pos error',
            'message_fa': ('موفق' if approved else (msg_fa or 'خطا')),
            'txn_status': txn,
            'error_name': err_name,
            'request_code': parsed.get('request_code'),
            'rrn': parsed.get('rrn'),
            'trace': parsed.get('seq'),
            'terminal': parsed.get('terminal'),
            'merchant': parsed.get('merchant'),
            'card_mask': parsed.get('card_mask'),
            'date': parsed.get('date'),
            'action': action,
        }
        # حالت ساده بدون متادیتای اضافی
        return out

# =============
# API برای ایمپورت در جنگو/پایتون
def sale_toman(ip: str, port: int, amount_toman: int, timeout_ms: int = 20000, invoice: str = "", debug: bool = False):
    return transact(ip, port, amount_toman * 10, timeout_ms, debug, 'sale', invoice)

def sale_rial(ip: str, port: int, amount_rial: int, timeout_ms: int = 20000, invoice: str = "", debug: bool = False):
    return transact(ip, port, amount_rial, timeout_ms, debug, 'sale', invoice)

def cancel(ip: str, port: int, timeout_ms: int = 20000, invoice: str = "", debug: bool = False):
    # amount برای کنسل استفاده نمی‌شود
    return transact(ip, port, 0, timeout_ms, debug, 'cancel', invoice)

class PosPasargadClient:
    def __init__(self, ip: str, port: int, timeout_ms: int = 20000, debug: bool = False):
        self.ip = ip
        self.port = port
        self.timeout_ms = timeout_ms
        self.debug = debug

    def sale_toman(self, amount_toman: int, invoice: str = ""):
        return sale_toman(self.ip, self.port, amount_toman, self.timeout_ms, invoice, self.debug)

    def sale_rial(self, amount_rial: int, invoice: str = ""):
        return sale_rial(self.ip, self.port, amount_rial, self.timeout_ms, invoice, self.debug)

    def cancel(self, invoice: str = ""):
        return cancel(self.ip, self.port, self.timeout_ms, invoice, self.debug)

if __name__ == '__main__':
    # استفاده: python pos_pasargad_client.py ip port amountToman [--rial] [--timeout-ms=20000] [--action=sale|cancel] [--invoice=XXXX]
    if len(sys.argv) < 4:
        print(json.dumps({'ok': False, 'message': 'usage: ip port amountToman [--rial] [--timeout-ms=20000] [--action=sale|cancel] [--invoice=XXXX]'}))
        sys.exit(0)
    ip = sys.argv[1]
    port = int(sys.argv[2])
    amount_input = int(sys.argv[3])
    amount_is_rial = any(a.lower() == '--rial' for a in sys.argv[4:])
    amount_rial = amount_input if amount_is_rial else amount_input * 10
    timeout_ms = 20000
    debug = False
    action = 'sale'
    invoice = ''
    for a in sys.argv[4:]:
        if a.lower().startswith('--timeout-ms='):
            try:
                timeout_ms = max(1000, min(180000, int(a.split('=',1)[1])))
            except:
                pass
        if a.lower() == '--debug':
            debug = True
        if a.lower() == '--rial':
            pass
        if a.lower().startswith('--action='):
            action = a.split('=',1)[1].lower()
        if a.lower().startswith('--invoice='):
            invoice = a.split('=',1)[1]
    try:
        res = transact(ip, port, amount_rial, timeout_ms, debug, action, invoice)
        print(json.dumps(res, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'ok': False, 'message': str(e)}))
