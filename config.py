import os

from pydantic import BaseSettings, Field


class TestsFields(BaseSettings):
    api_id: str = Field(None, env="tests_api_id")
    api_hash: str = Field(None, env="tests_api_hash")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Config(BaseSettings):
    admins: list[int]
    debugging: bool = Field(False, alias="WEB_APP_DEBUG")
    web_app_port: int = 5000
    web_app_host: str = "localhost"
    bot_token: str
    http_proxy_url: str
    proxy_auth: str
    chatgpt_passwords: list
    chatgpt_api_key: str
    chat_timeout: int = 60
    openai_url: str = "https://api.openai.com/v1/completions"
    bot_name: str
    tests = TestsFields()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config: Config
config = Config()
