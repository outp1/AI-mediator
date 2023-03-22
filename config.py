from typing import Literal

from pydantic import BaseSettings, Field


class BaseConfigSection(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class TestsFields(BaseConfigSection):
    api_id: str = Field(None, env="tests_api_id")
    api_hash: str = Field(None, env="tests_api_hash")


class LoggingFields(BaseConfigSection):
    logging_file: str
    console_logging_level: Literal["DEBUG", "INFO", "ERROR", "CRITICAL"]
    bot_token: str = Field("", env="logging_bot_token")
    admins: list[int]


class DatabaseFields(BaseConfigSection):
    host: str = Field("", env="pg_host")
    port: int = Field(5432, env="pg_port")
    login: str = Field("", env="pg_login")
    password: str = Field("", env="pg_password")
    database: str = Field("", env="pg_dbname")


class Config(BaseConfigSection):
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
    logging = LoggingFields()
    db = DatabaseFields()


config: Config
config = Config()
