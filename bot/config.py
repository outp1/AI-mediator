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
        self.proxy_url = env.str("PROXY_URL", "")
        self.proxy_password = env.str("PROXY_PASSWORD", "")
        self.misc_secret_key = env.str("MISC_SECRET_KEY", "secret")
        self.chatgpt_password = env.str("CHATGPT_PASSWORD")

config = Config()


