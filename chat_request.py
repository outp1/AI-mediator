import json
import logging

import aiohttp


class OpenAIRequest:
    def __init__(self, config, api_key):
        self.logger = logging.getLogger(__name__)
        self.proxy = f"http://{config.proxy_auth}@{config.http_proxy_url}"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self.url = "https://api.openai.com/v1/completions"

    async def send_request(
        self,
        prompt,
        temperature=0,
        max_tokens=2024,
        model="text-davinci-003",
        user=None,
    ):
        try:
            self.logger.info(f"prompt: {prompt}")
            data = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if user:
                data["user"] = str(user)
            data = json.dumps(data)
            self.logger.info(f"sending request with data: {data}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url,
                    headers=self.headers,
                    data=data,
                    proxy=self.proxy,
                ) as resp:
                    if resp.status == 200:
                        text = await resp.json()
                        text = text["choices"][0]["text"]
                        return text
                    else:
                        self.logger.error(
                            f"failed to get response with status code: {resp.status}"
                        )
                        return f"failed to get response with status code: {resp.status}"
        except Exception as e:
            self.logger.exception(f"failed to send request: {e}")
            return f"failed to send request: {e}"

    async def get_models_list(self):
        models = await self._request_models()
        if isinstance(models, dict):
            return models["data"]
        else:
            return None

    async def _request_models(self):
        try:
            self.logger.info("Getting list of models")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.openai.com/v1/models",
                    headers=self.headers,
                    proxy=self.proxy,
                ) as resp:
                    if resp.status == 200:
                        models = await resp.json()
                        return models
                    else:
                        self.logger.error(
                            f"failed to get response with status code: {resp.status}"
                        )
                        return f"failed to get response with status code: {resp.status}"
        except Exception as e:
            self.logger.exception(f"failed to send request: {e}")
            return f"failed to send request: {e}"

    async def get_model(self, model):
        try:
            self.logger.info(f"Getting model {model}")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.openai.com/v1/models/{model}",
                    headers=self.headers,
                    proxy=self.proxy,
                ) as response:
                    self.logger.info(
                        f"Received response with status code: {response.status}"
                    )
                    if response.status == 200:
                        model_info = response.json()
                        return model_info
                    else:
                        self.logger.error(
                            f"Failed to get response with status code: {response.status}"
                        )
                        return f"Failed to get response with status code: {response.status}"
        except Exception as e:
            self.logger.exception(f"Failed to get model: {e}")
            return None
