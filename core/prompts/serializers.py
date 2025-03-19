from rest_framework import serializers

class GeneratePromptSerializer(serializers.Serializer):
    user_input = serializers.CharField(required=True, help_text="3D 모델을 생성하기 위한 사용자 입력")