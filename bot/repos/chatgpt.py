import json
import logging
from traceback import format_exc

import aiohttp

from config import config

logger = logging.getLogger("telegram_bot.OpenAIRepo")


class OpenAIRepo:
    def __init__(self):
        self.proxy = f"http://{config.proxy_auth}@{config.http_proxy_url}"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.chatgpt_api_key}",
        }
        self.logger = logging.getLogger("telegram_bot.OpenAIRepo")

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, *excinfo):
        await self.session.close()

    async def send_request(
        self,
        prompt,
        temperature=0.7,
        max_tokens=2024,
        model="gpt-3.5-turbo",
        user=None,
        disable_proxy: bool = False,
    ):
        try:
            prompt = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "messages": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if user:
                data["user"] = str(user)

            kwargs = {"data": json.dumps(data)}

            if not disable_proxy:
                kwargs["proxy"] = self.proxy
            self.logger.debug("Sending request to OpenAI")
            async with self.session.post(config.openai_url, **kwargs) as resp:
                if resp.status != 200:
                    logger.error(
                        f"failed to get response with status code: {resp.status}"
                    )
                    return f"failed to get response with status code: {resp.status}"

                result = await resp.json()
                self.logger.debug(f"Response is: \n{result}")
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(format_exc())
            return f"failed to send request: {e}"
