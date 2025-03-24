from django.db import models
from articles.models import Article

# Create your models here.
class Evaluation(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    evaluation_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation for Article {self.article.id}"