import json

import aiohttp

from config import config


class OpenAIRepo:
    def __init__(self):
        self.proxy = f"http://{config.proxy_auth}@{config.http_proxy_url}"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.chatgpt_api_key}",
        }
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def send_request(
        self,
        prompt,
        temperature=0,
        max_tokens=2024,
        model="text-davinci-003",
        user=None,
        disable_proxy: bool = False,
    ):
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if user:
                data["user"] = str(user)

            kwargs = {"data": json.dumps(data)}

            if not disable_proxy:
                kwargs["proxy"] = self.proxy
            async with self.session.post(config.openai_url, **kwargs) as resp:
                print(resp)
                if resp.status != 200:
                    return f"failed to get response with status code: {resp.status}"

                return (await resp.json())["choises"][0]["text"]
        except Exception as e:
            return f"failed to send request: {e}"

    def __del__(self):
        self.session.close()  # TODO: fix
