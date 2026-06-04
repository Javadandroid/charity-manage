# from persianttsfarsi import PersianTTS

# # استفاده دقیق طبق مستندات PyPI
# tts = PersianTTS()
# tts.synthesize("سلام دنیا! این یک مثال از تبدیل متن به گفتار فارسی است.", "output.mp3")
# print("Saved:", "output.mp3")

import os, sys
import azure.cognitiveservices.speech as speechsdk

key = os.environ.get("AZURE_SPEECH_KEY")
region = os.environ.get("AZURE_SPEECH_REGION")
if not key or not region:
    print("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION env vars."); sys.exit(1)

speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
speech_config.speech_synthesis_language = "fa-IR"
# اگر خطا داد، نام voice را مشخص کنید (مثلاً):
# speech_config.speech_synthesis_voice_name = "fa-IR-DilaraNeural"

audio_config = speechsdk.audio.AudioOutputConfig(filename="azure_test.mp3")
synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

text = "شماره پنجاه و هفت. غرفه فست فود"
result = synthesizer.speak_text_async(text).get()
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Saved: azure_test.mp3")
else:
    print("Synthesis failed:", result.reason, result.cancellation_details if hasattr(result, 'cancellation_details') else '')