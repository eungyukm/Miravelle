from django import forms
from .models import Article

# 게시물 작성 Form
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "image", "title", "tags", "model_seed", "model_prompt", "texture_prompt"
            ]
        read_only = ("title", "model_seed")