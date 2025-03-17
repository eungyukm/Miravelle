# from django.test import TestCase  # Django의 테스트 프레임워크
# from django.contrib.auth import get_user_model  # 사용자 모델
# from rest_framework.test import APIClient  # REST API 테스트용
# from django.urls import reverse  # URL 패턴 역변환
# # 테스트 할 articles 앱 모델
# from workspace.models import MeshModel  # 메시 모델
# from articles.models import Article, Like  # 게시글, 좋아요 모델

# # 테스트 실행 명령어
# # python manage.py test core.articles.tests          테스트만 실행
# # python manage.py test core.articles.tests -v 2     제세한 출력과 함께 실행




# class ArticleTests(TestCase):
#     """
#     게시글 관련 테스트 케이스들을 포함하는 클래스입니다.
#     각 테스트 메서드마다 setUp에서 생성된 새로운 환경에서 실행됩니다.
#     """
    
#     def setUp(self):  
#         """
#         각 테스트 메서드 실행 전에 필요한 초기 데이터를 설정합니다.
#         데이터베이스는 매 테스트마다 새로 생성됩니다.
#         """
#         # 1. 테스트용 사용자 생성
#         self.user = get_user_model().objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='testpass123'
#         )
        
#         # 2. 테스트용 메시 모델 생성
#         self.mesh_model = MeshModel.objects.create(
#             user=self.user,
#             job_id="test123",
#             create_prompt="Test prompt"
#         )
        
#         # 3. 테스트용 게시글 생성
#         self.article = Article.objects.create(
#             user_id=self.user,
#             title="Test Article",
#             model_prompt="Test model prompt",
#             texture_prompt="Test texture prompt",
#             job=self.mesh_model
#         )
        
#         # 4. API 테스트를 위한 클라이언트 설정
#         self.client = APIClient()

#     def test_article_creation(self):
#         """
#         게시글 생성 테스트
#         - 제목이 올바르게 저장되었는지
#         - 초기 상태가 'processing'인지
#         - model_seed가 생성되었는지
#         """
#         self.assertEqual(self.article.title, "Test Article")  # 제목 확인
#         self.assertEqual(self.article.status, "processing")  # 상태 확인
#         self.assertTrue(self.article.model_seed > 0)  # model_seed 생성이 참인지 확인
        
#     def test_like_creation(self):
#         """
#         좋아요 기능 테스트
#         - 좋아요 객체가 올바르게 생성되는지
#         - 좋아요 타입이 정확히 저장되는지
#         """
#         like = Like.objects.create(
#             user=self.user,
#             article=self.article,
#             like_type="❤️"
#         )
#         self.assertEqual(like.like_type, "❤️")  # 좋아요 타입 확인
        
#     def test_article_list_view(self):
#         """
#         게시글 목록 조회 테스트
#         - 로그인한 사용자가 목록을 볼 수 있는지
#         - 응답 상태 코드가 200(성공)인지
#         """
#         self.client.login(username='testuser', password='testpass123')
#         response = self.client.get(reverse('articles:main')) # 결과: '/articles/'
#         self.assertEqual(response.status_code, 200)  # 실제 값 response.status_code와 예상 값 200 비교
        
#     def test_article_detail_view(self):
#         """
#         게시글 상세 조회 테스트
#         - 특정 게시글을 정상적으로 조회할 수 있는지
#         - 응답 상태 코드가 200(성공)인지
#         """
#         self.client.login(username='testuser', password='testpass123')
#         response = self.client.get(
#             reverse('articles:articledetail', kwargs={'id': self.article.id}) # 결과: '/articles/1/'
#         )                                            
#         self.assertEqual(response.status_code, 200)  # 실제 값 response.status_code와 예상 값 200 비교
 