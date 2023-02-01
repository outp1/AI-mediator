import requests
import json
import logging


class OpenAIRequest:
    def __init__(self, config, api_key):
        self.logger = logging.getLogger(__name__)
        self.proxies = {
            "http": f"http://{config.proxy_auth}@{config.http_proxy_url}",
            "https": f"http://{config.proxy_auth}@{config.http_proxy_url}",
        }
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self.url = "https://api.openai.com/v1/completions"

    def send_request(
        self, prompt, temperature=0, max_tokens=4000, model="text-davinci-003"
    ):
        try:
            self.logger.info(f"Prompt: {prompt}")
            data = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            data = json.dumps(data)
            self.logger.info(f"Sending request with data: {data}")
            response = requests.post(
                self.url, data=data, headers=self.headers, proxies=self.proxies
            )
            self.logger.info(
                f"Received response with status code: {response.status_code}"
            )
            if response.status_code == 200:
                text = response.json()
                text = text["choices"][0]["text"]
                return text
            else:
                self.logger.error(
                    f"Failed to get response with status code: {response.status_code}"
                )
                return (
                    f"Failed to get response with status code: {response.status_code}"
                )
        except Exception as e:
            self.logger.exception(f"Failed to send request: {e}")
            return None
