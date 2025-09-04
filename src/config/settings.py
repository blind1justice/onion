from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str = 'practice'
    db_password: str = 'superpractice'
    db_name: str = 'practice'
    db_host: str = 'db'
    db_port: int = 5432

    resend_api_key: str
    resend_from_email: str = "Acme <onboarding@resend.dev>"

    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    base_url: str
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str
    celery_result_backend: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:"
            f"{self.db_password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env" 


settings = Settings()
