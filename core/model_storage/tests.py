from django.test import TestCase, Client
from django.urls import reverse
from workspace.models import MeshModel
from django.contrib.auth import get_user_model

class PublishArticleTestCase(TestCase):
    def setUp(self):
        # 테스트용 유저 생성
        self.user = get_user_model().objects.create_user(
            username='test0', password='pasword!@#$'
        )

        # 테스트용 MeshModel 생성
        self.mesh = MeshModel.objects.create(
            user=self.user,
            job_id="test-2608-7e8b-bf5f-4b7b8a6e0e64",
            status="completed",
            create_prompt="Test Prompt"
        )

        # 클라이언트 생성
        self.client = Client()

    def test_publish_article(self):
        url = reverse('publish_article', args=[self.mesh.id])  # URL 생성
        response = self.client.post(url)  # POST 요청 수행

        # 상태 코드 200 확인
        self.assertEqual(response.status_code, 200)
        self.assertIn("게시글이 성공적으로 공개되었습니다.", response.content.decode())

        # Article이 생성되었는지 확인
        from articles.models import Article
        article = Article.objects.get(job=self.mesh)

        self.assertEqual(article.title, f"New Mesh: {self.mesh.job_id}")
        self.assertEqual(article.user_id, self.mesh.user)
        self.assertEqual(article.model_prompt, self.mesh.create_prompt)

        print(f"게시 성공 → Article ID: {article.id}")