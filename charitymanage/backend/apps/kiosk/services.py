import os
import asyncio
import edge_tts
from django.conf import settings

class TTSService:
    """
    سرویس هوش مصنوعی تبدیل متن به گفتار (TTS) با استفاده از Microsoft Edge.
    الگوی Singleton برای مدیریت ارتباطات.
    """
    _instance = None
    
    # صدای پیش‌فرض فارسی دیلارا (صدای زنانه بسیار طبیعی)
    DEFAULT_VOICE = "fa-IR-DilaraNeural"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTSService, cls).__new__(cls)
        return cls._instance

    async def _generate_audio_async(self, text: str, file_path: str):
        """متد غیرهمگام تولید فایل صوتی"""
        communicate = edge_tts.Communicate(text, self.DEFAULT_VOICE)
        await communicate.save(file_path)

    def generate_invoice_audio(self, invoice_number: str) -> str:
        """
        دریافت شماره فاکتور (مانند inv000012) و تبدیل آن به گفتار.
        برگرداندن آدرس URL نسبی فایل صوتی.
        """
        # تمیز کردن شماره فاکتور (حذف پیشوند inv و تبدیل صفرها)
        clean_number = invoice_number.lower().replace('inv', '').lstrip('0')
        if not clean_number:
            clean_number = "صفر"
        
        # متن مورد نظر برای خواندن
        text_to_speak = f"شماره فاکتور {clean_number} آماده تحویل است."
        
        # مسیر ذخیره فایل صوتی
        media_root = settings.MEDIA_ROOT
        tts_dir = os.path.join(media_root, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        
        file_name = f"invoice_{invoice_number}.mp3"
        file_path = os.path.join(tts_dir, file_name)
        
        # اگر فایل از قبل موجود است، فقط URL آن را برگردان
        if os.path.exists(file_path):
            return f"{settings.MEDIA_URL}tts/{file_name}"

        # اجرای تولید فایل به صورت همگام در صورت فراخوانی در محیط معمولی جنگو
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        loop.run_until_complete(self._generate_audio_async(text_to_speak, file_path))
        
        return f"{settings.MEDIA_URL}tts/{file_name}"
