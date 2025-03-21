import os
from django.conf import settings
from threading import Lock

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class AzureKeyManager:
    """Azure Key Vault 및 로컬 환경 키를 관리하는 싱글톤 클래스"""

    _instance = None
    _lock = Lock()  # Thread-safe 보장

    def __new__(cls):
        if not cls._instance:
            with cls._lock:  # 멀티스레드 환경에서도 한 번만 초기화
                if not cls._instance:
                    cls._instance = super(AzureKeyManager, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """로컬 또는 배포 환경에 맞는 Secret을 가져와 저장"""
        if settings.IS_LOCAL_ENV == False:
            self._load_from_azure_key_vault()
        else:
            self._load_from_env_file()

    def _load_from_env_file(self):
        """로컬 환경: .env 파일에서 값 로드"""
        load_dotenv()
        print("로컬 환경 - .env 파일 로드")

        self.storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.storage_account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        self.container_name = os.getenv("AZURE_CONTAINER_NAME")
        self.connection_string = os.getenv("AZURE_CONNECTION_STRING")
        self.meshy_api_key = os.getenv("MESHY_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def _load_from_azure_key_vault(self):
        """배포 환경: Azure Key Vault에서 Secret 가져오기"""
        key_vault_name = "miravelle-key"
        key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"
        print("배포 환경 - Azure Key Vault에서 Secret 로드")

        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=key_vault_uri, credential=self.credential)

        self.storage_account_name = self._get_secret("azure-storage-account-name")
        self.storage_account_key = self._get_secret("azure-storage-account-key")
        self.container_name = self._get_secret("azure-container-name")
        self.connection_string = self._get_secret("azure-connection-string")
        self.meshy_api_key = self._get_secret("meshy-api-key", strip=True)
        self.openai_api_key = self._get_secret("OPENAI-API-KEY")

    def _get_secret(self, secret_name, strip=False):
        """Key Vault에서 Secret을 안전하게 가져오는 메서드"""
        try:
            secret_value = self.client.get_secret(secret_name).value
            return secret_value.strip() if strip else secret_value
        except Exception as e:
            print(f"Error fetching secret '{secret_name}': {e}")
            return None

    @classmethod
    def get_instance(cls):
        """싱글톤 인스턴스 반환"""
        return cls()


# 사용 예시
# azure_keys = AzureKeyManager.get_instance()
# print(azure_keys.connection_string)
