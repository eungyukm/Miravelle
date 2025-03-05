# forms.py
from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'model_prompt', 'texture_prompt', 'image', 'tags']  # 폼에서 수정할 필드를 지정
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'model_prompt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'texture_prompt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 선택 사항: 필드 속성 추가 (예: required 설정)
        self.fields['title'].required = True  # 제목 필드 필수 설정
        self.fields['image'].required = True  # 이미지 필드 필수 설정