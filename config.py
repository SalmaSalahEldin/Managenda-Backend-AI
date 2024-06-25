# from pydantic_settings import BaseSettings
# from pydantic import EmailStr
#
#
#
# class Settings(BaseSettings):
#     MAIL_USERNAME: str
#     MAIL_PASSWORD: str
#     MAIL_FROM: EmailStr
#     MAIL_PORT: int
#     MAIL_SERVER: str
#     MAIL_FROM_NAME: str = "Support Team"
#     MAIL_STARTTLS: bool = True
#     MAIL_SSL_TLS: bool = False
#     PINECONE_API_KEY: str
#     OPENAI_API_KEY: str
#     class Config:
#         env_file = ".env"
#
# settings = Settings()