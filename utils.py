import requests

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
        text = result["result"]["translated_text"]
        return text
