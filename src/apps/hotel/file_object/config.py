from pydantic import SecretStr
from pydantic_settings import BaseSettings


class S3Settings(BaseSettings):
    bucket_name: str = "hotel-app-bucket"
    sample_files_prefix: str = "sample"
    s3_endpoint: str = "http://localhost:9000"
    s3_endpoint_public: str = "http://localhost:9000"
    s3_access_key: str = "minio-user"
    s3_secret_key: SecretStr = SecretStr("minio-password")
    connection_pool_size: int = 30
    s3_file_download_size: int = 2097152
