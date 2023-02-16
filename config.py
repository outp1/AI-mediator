import os

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
        env_file = 'tests/bot_tests/.env'
        env_file_encoding = 'utf-8'


def prepare_environment():
    os.environ["PROJECT_NAME"] = "ChatGPT_mediators"
    os.environ["BOT_NAME"] = "ChatGPT_DEMO"
    os.environ["BOT_TOKEN"] = "123:abc"
    os.environ["HTTP_PROXY_URL"] = "0.0.0.0:8000"
    os.environ["PROXY_AUTH"] = "user:password"
    os.environ["CHATGPT_PASSWORD"] = "123"
    os.environ["CHATGPT_API_KEY"] = ""


config: Config
try:
    config = Config()
except Exception:
    prepare_environment()  # fixme
    config = Config()
