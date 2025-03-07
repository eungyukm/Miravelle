from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from threading import Lock


class AzureKeyManager:
    """Azure Key Vault의 Key들을 싱글톤으로 관리하는 클래스"""
    
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
        """Key Vault에서 Secret을 가져와서 저장"""
        key_vault_name = "miravelle-key"
        key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"

        # 인증 설정
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=key_vault_uri, credential=self.credential)

        # Secret 가져오기
        self.storage_account_name = self._get_secret("azure-storage-account-name")
        self.storage_account_key = self._get_secret("azure-storage-account-key")
        self.container_name = self._get_secret("azure-container-name")
        self.connection_string = self._get_secret("azure-connection-string")
        self.meshy_api_key = self._get_secret("mehsy-api-key")

    def _get_secret(self, secret_name):
        """Key Vault에서 Secret을 안전하게 가져오는 메서드"""
        try:
            return self.client.get_secret(secret_name).value
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
