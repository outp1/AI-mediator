import os

import environs


class Config:
    def __init__(self):
        env = environs.Env()
        env.read_env(".env")
        self.web_app_debug = env.bool("WEB_APP_DEBUG", False)
        self.web_app_port = env.int("WEB_APP_PORT", 5000)
        self.web_app_host = env.str("WEB_APP_HOST", "localhost")
        self.bot_token = env.str("BOT_TOKEN", "")
        self.http_proxy_url = env.str("HTTP_PROXY_URL", "")
        self.proxy_auth = env.str("PROXY_AUTH", "")
        self.chatgpt_password = env.str("CHATGPT_PASSWORD")
        self.chatgpt_api_key = env.str("CHATGPT_API_KEY")

config = Config()


