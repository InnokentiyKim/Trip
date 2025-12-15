from pydantic_settings import BaseSettings


class S3Settings(BaseSettings):
    bucket_name: str = "hotel-app-bucket"
    sample_files_prefix: str = "sample"
    s3_endpoint: str = "http://minio:9000"
    s3_endpoint_public: str = "http://localhost:9000"
