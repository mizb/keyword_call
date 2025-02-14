# keyword_call
可用于dify-on-wechat和chatgpt-on-wechat的插件，可设置多个关键字，根据不同关键字调用不同的API

当前只支持两种调用方式，一种是cloudflare的文生图，一种是openai的api，后续再持续增加api接入及完善



安装后，记得cp config.json.template config.json

config.json 配置说明
```bash
{
  "#invoking_reply#": "🪄✨ 正在为您召唤魔法，稍等一会儿，马上就好。",
  "#error_reply#": "😮‍💨看起来像是服务器在做深呼吸，稍等一下，它会回来的。",
  "$$":{
        "api_type": "cf-image",
        "open_ai_api_base": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell",
        "open_ai_api_key":  "api-key",
        "open_ai_model": "@cf/bytedance/stable-diffusion-xl-lightning",
        "prompt":  "A realistic and highly detailed scene"
  },
  "&&":{
        "api_type": "openai",
        "open_ai_api_base": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions",
        "open_ai_api_key":  "api-key",
        "open_ai_model": "@cf/meta/llama-3.1-70b-instruct",
        "prompt":  "你是一个专业的律师，你给提供专业的法律意见"
  }
}


```


