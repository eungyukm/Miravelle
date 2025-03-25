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
        
        # 테스트용 메시 모델들 생성 (총 5개)
        self.mesh_models = []
        for i in range(5):
            mesh_model = MeshModel.objects.create(
                job_id=f"test{i+1}",
                user=self.user
            )
            self.mesh_models.append(mesh_model)
            
            # 각 메시 모델에 대한 메시 에셋 생성
            MeshAsset.objects.create(
                mesh_model=mesh_model,
                title=f"테스트 메시 에셋 {i+1}",
                prompt=f"테스트 프롬프트 {i+1}"
            )

    def test_asset_creation(self):
        """에셋이 올바르게 생성되는지 테스트"""
        self.assertEqual(self.asset.title, "테스트 에셋")
        self.assertEqual(self.asset.content, "테스트 내용")
        self.assertEqual(self.asset.user, self.user)

    def test_mesh_asset_creation(self):
        """메시 에셋이 올바르게 생성되는지 테스트"""
        self.assertEqual(self.mesh_models[0].job_id, "test1")
        self.assertEqual(self.mesh_models[1].job_id, "test2")
        self.assertEqual(self.mesh_models[2].job_id, "test3")
        self.assertEqual(self.mesh_models[3].job_id, "test4")
        self.assertEqual(self.mesh_models[4].job_id, "test5")

    def test_asset_list_view(self):
        """에셋 목록 뷰 테스트"""
        # 로그인
        self.client.login(username='testuser', password='testpass123')
        
        # 에셋 목록 페이지 접근
        response = self.client.get(reverse('assets:asset_list'))
        
        # 응답 상태 코드가 200인지 확인
        self.assertEqual(response.status_code, 200)
        
        # 템플릿에 메시 에셋 정보가 포함되어 있는지 확인
        self.assertContains(response, "test1")
        self.assertContains(response, "test2")
        self.assertContains(response, "test3")
        self.assertContains(response, "test4")
        self.assertContains(response, "test5")

    def test_asset_list_view_unauthorized(self):
        """비로그인 사용자의 에셋 목록 접근 테스트"""
        # 로그아웃 상태에서 접근
        response = self.client.get(reverse('assets:asset_list'))
        
        # 로그인 페이지로 리다이렉트되는지 확인
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/users/login/'))

    def test_asset_list_pagination(self):
        """에셋 목록 페이징 테스트"""
        # 로그인
        self.client.login(username='testuser', password='testpass123')
        
        # 첫 페이지 테스트 (4개 표시)
        response = self.client.get(reverse('assets:asset_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['assets']), 4)  # 첫 페이지에 4개 표시
        
        # 두 번째 페이지 테스트 (1개 표시)
        response = self.client.get(reverse('assets:asset_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assets']), 1)  # 두 번째 페이지에 1개 표시

    def test_invalid_page_handling(self):
        """잘못된 페이지 번호 처리 테스트"""
        self.client.login(username='testuser', password='testpass123')
        
        # 존재하지 않는 페이지 번호 테스트
        response = self.client.get(reverse('assets:asset_list') + '?page=999')
        self.assertEqual(response.status_code, 200)  # 에러 대신 마지막 페이지 표시
        
        # 잘못된 페이지 번호 형식 테스트
        response = self.client.get(reverse('assets:asset_list') + '?page=abc')
        self.assertEqual(response.status_code, 200)  # 에러 대신 첫 페이지 표시
