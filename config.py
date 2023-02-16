from pydantic import BaseSettings, Field


class Config(BaseSettings):
    debugging: bool = Field(False, alias="WEB_APP_DEBUG")
    web_app_port: int = 5000
    web_app_host: str = "localhost"
    bot_token: str
    http_proxy_url: str
    proxy_auth: str
    chatgpt_password: str
    chatgpt_api_key: str
    chat_timeout: int = 60
    openai_url: str = "https://api.openai.com/v1/completions"

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Config()
