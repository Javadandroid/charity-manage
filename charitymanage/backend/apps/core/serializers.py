from rest_framework import serializers
from .models import Font, SystemSetting

class FontSerializer(serializers.ModelSerializer):
    class Meta:
        model = Font
        fields = '__all__'

class SystemSettingSerializer(serializers.ModelSerializer):
    primary_font = FontSerializer(read_only=True)
    
    class Meta:
        model = SystemSetting
        fields = '__all__'
