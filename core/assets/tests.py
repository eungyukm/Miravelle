from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Asset, MeshAsset
from workspace.models import MeshModel

class AssetTests(TestCase):
    def setUp(self):
        # 테스트용 사용자 생성
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 테스트용 클라이언트 설정
        self.client = Client()
        
        # 테스트용 에셋 생성
        self.asset = Asset.objects.create(
            user=self.user,
            title="테스트 에셋",
            content="테스트 내용",
            file_path="/path/to/test.glb"
        )
        
        # 테스트용 메시 모델 생성
        self.mesh_model = MeshModel.objects.create(
            job_id="test123",
            user=self.user
        )
        
        # 테스트용 메시 에셋 생성
        self.mesh_asset = MeshAsset.objects.create(
            mesh_model=self.mesh_model,
            title="테스트 메시 에셋",
            prompt="테스트 프롬프트"
        )

    def test_asset_creation(self):
        """에셋이 올바르게 생성되는지 테스트"""
        self.assertEqual(self.asset.title, "테스트 에셋")
        self.assertEqual(self.asset.content, "테스트 내용")
        self.assertEqual(self.asset.user, self.user)

    def test_mesh_asset_creation(self):
        """메시 에셋이 올바르게 생성되는지 테스트"""
        self.assertEqual(self.mesh_asset.title, "테스트 메시 에셋")
        self.assertEqual(self.mesh_asset.prompt, "테스트 프롬프트")
        self.assertEqual(self.mesh_asset.mesh_model.job_id, "test123")

    def test_asset_list_view(self):
        """에셋 목록 뷰 테스트"""
        # 로그인
        self.client.login(username='testuser', password='testpass123')
        
        # 에셋 목록 페이지 접근
        response = self.client.get(reverse('assets:asset_list'))
        
        # 응답 상태 코드가 200인지 확인
        self.assertEqual(response.status_code, 200)
        
        # 템플릿에 메시 에셋 정보가 포함되어 있는지 확인
        self.assertContains(response, "test123")  # job_id 확인
        self.assertContains(response, "테스트 프롬프트")  # prompt 확인

    def test_asset_list_view_unauthorized(self):
        """비로그인 사용자의 에셋 목록 접근 테스트"""
        # 로그아웃 상태에서 접근
        response = self.client.get(reverse('assets:asset_list'))
        
        # 로그인 페이지로 리다이렉트되는지 확인
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/users/login/'))
