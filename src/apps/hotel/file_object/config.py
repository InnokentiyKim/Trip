from pydantic_settings import BaseSettings


class S3Settings(BaseSettings):
    bucket_name: str
    sample_files_prefix: str
    s3_endpoint: str
    s3_endpoint_public: str
