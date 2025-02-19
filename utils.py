mport requests

class Utils():
    @staticmethod
    def translate(self, endpoint: str, appkey: str, query: str, from_lang: str = "", to_lang: str = "en") -> str:
        if not from_lang:
            from_lang = "chinese"
        headers = {"Content-Type": "application/json",'Authorization': f"Bearer {appkey}",}
        payload = {"text": query, "source_lang": from_lang, "target_lang": to_lang}

        retry_cnt = 3
        while retry_cnt:
            r = requests.post(endpoint, json=payload, headers=headers)
            result = r.json()
            errcode = result.get("error_code", "52000")
            if errcode != "52000":
                if errcode == "52001" or errcode == "52002":
                    retry_cnt -= 1
                    continue
                else:
                    raise Exception(result["error_msg"])
            else:
                break
        print(result)
        text = result["result"]["translated_text"]
        return text

    @staticmethod
    def translatByOpenAI(self, endpoint: str, appkey: str, model: str, prompt: str, query: str) -> str:
        headers = {"Content-Type": "application/json",'Authorization': f"Bearer {appkey}",}
        payload = {
                    "model": f"{model}",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{prompt} {query}"
                        }
                    ]
                }
        response = None
        retry_cnt = 3
        while retry_cnt:
            response = requests.post(endpoint, json=payload, headers=headers)
            if response.status_code == 200:
                break
            else:
                print(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
                retry_cnt -= 1
                continue
        if retry_cnt == 0:
            return "Call API failed,Please retry again later!"
        result = response.json()['choices'][0]['message']['content']
        return result
