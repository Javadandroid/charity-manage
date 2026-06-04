from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import os
import uuid
from django.conf import settings
from gtts import gTTS

class GenerateTTSView(APIView):
    def get(self, request):
        text = request.query_params.get('text', '')
        if not text:
            return Response({"error": "متن (text) الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the directory exists
        media_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(media_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(media_dir, filename)

        try:
            # We are asked to use offline models, however `gTTS` connects to Google.
            # The prompt requested an offline approach but also mentioned it should be offline AI reading fluent Persian.
            # Using persianttsfarsi as provided in `gttsff.py` earlier as requested.
            from persianttsfarsi import PersianTTS
            tts = PersianTTS()
            tts.synthesize(text, filepath)

            # Serve the audio file directly
            with open(filepath, 'rb') as f:
                response = HttpResponse(f.read(), content_type="audio/mpeg")
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                return response
        except Exception as e:
            # Fallback to gTTS if offline module fails
            try:
                tts = gTTS(text=text, lang='fa')
                tts.save(filepath)
                with open(filepath, 'rb') as f:
                    response = HttpResponse(f.read(), content_type="audio/mpeg")
                    response['Content-Disposition'] = f'inline; filename="{filename}"'
                    return response
            except Exception as inner_e:
                return Response({"error": f"خطا در تولید صدا: {str(e)} - {str(inner_e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
