from rest_framework import serializers
from .models import EnhancedPrompt

class GeneratePromptSerializer(serializers.Serializer):
    user_input = serializers.CharField(required=True, help_text="3D 모델을 생성하기 위한 사용자 입력")


class EnhancedPromptInputSerializer(serializers.Serializer):
    """
    프롬프트 개선 API에 대한 입력 시리얼라이저입니다.
    """
    prompt = serializers.CharField(required=True, help_text="개선할 원본 프롬프트")
    user_id = serializers.IntegerField(required=False, help_text="사용자 ID (인증된 경우)")


class EnhancedPromptSerializer(serializers.ModelSerializer):
    """
    개선된 프롬프트 모델의 시리얼라이저입니다.
    """
    enhanced_prompts_list = serializers.SerializerMethodField()
    scores_dict = serializers.SerializerMethodField()
    
    class Meta:
        model = EnhancedPrompt
        fields = [
            'id', 'original_prompt', 'enhanced_prompts_list', 
            'selected_prompt', 'selection_reason', 'scores_dict',
            'created_at', 'used_for_generation'
        ]
    
    def get_enhanced_prompts_list(self, obj):
        """
        JSON 형식의 enhanced_prompts 필드를 파이썬 리스트로 변환합니다.
        """
        import json
        try:
            return json.loads(obj.enhanced_prompts)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def get_scores_dict(self, obj):
        """
        JSON 형식의 scores 필드를 파이썬 딕셔너리로 변환합니다.
        """
        import json
        try:
            return json.loads(obj.scores)
        except (json.JSONDecodeError, TypeError):
            return {}