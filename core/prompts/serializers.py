from rest_framework import serializers

class GenerateMeshRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(
        help_text="생성할 3D 모델에 대한 프롬프트 (예: '귀여운 강아지')."
    )
    art_style = serializers.CharField(
        default="realistic",
        required=False,
        help_text="모델의 스타일 (예: 'realistic', 'cartoon'). 기본값은 'realistic'입니다."
    )

    def validate_art_style(self, value):
        """art_style 유효성 검사."""
        allowed_styles = ["realistic", " artoon", "abstract", "horror", "industrial aesthetic", "game figure"]  # 허용되는 스타일 목록
        if value not in allowed_styles:
            raise serializers.ValidationError(
                f"잘못된 art_style입니다. 다음 중 하나를 선택하세요: {', '.join(allowed_styles)}"
            )
        return value