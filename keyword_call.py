# encoding:utf-8
import io
import json
import base64
import re
import os
import html
from urllib.parse import urlparse

import requests

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *
from .utils import Utils

@plugins.register(
    name="KeywordCall",
    desire_priority=10,
    hidden=False,
    desc="Call different APIs based on keywords",
    version="0.0.1",
    author="pigracing",
)
class KeywordCall(Plugin):

    def __init__(self):
        super().__init__()
        try:
            self.config = super().load_config()
            if not self.config:
                self.config = self._load_config_template()
            self.invoking_reply = self.config.get("#invoking_reply#","🪄✨ 正在为您召唤魔法，稍等一会儿，马上就好。")
            self.error_reply = self.config.get("#error_reply#","😮💨看起来像是服务器在做深呼吸，稍等一下，它会回来的。")
            logger.info(f"[KeywordCall] inited, config={self.config}")
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        except Exception as e:
            logger.error(f"[KeywordCall] 初始化异常：{e}")
            raise "[KeywordCall] init failed, ignore "

    def on_handle_context(self, e_context: EventContext, retry_count: int = 0):
        try:
            context = e_context["context"]
            if context.type != ContextType.TEXT:
                return
            content = context.content.strip()
            logger.debug("[keyword] on_handle_context. content: %s" % content)
            keywords = list(self.config.keys())
            matching_keywords = [keyword for keyword in keywords if content.startswith(keyword)]
            if matching_keywords:
                print(f"匹配到以关键字开头：{matching_keywords[0]}")
                print(f"匹配到以关键字配置内容：{self.config[matching_keywords[0]]}")
                if retry_count == 0:
                    logger.debug("[KeywordCall] on_handle_context. content: %s" % content)
                    reply = Reply(ReplyType.TEXT, self.invoking_reply)
                    channel = e_context["channel"]
                    channel.send(reply, context)
                self.api_type = self.config[matching_keywords[0]].get("api_type", "")
                self.open_ai_api_base = self.config[matching_keywords[0]].get("open_ai_api_base", "")
                self.open_ai_api_key = self.config[matching_keywords[0]].get("open_ai_api_key", "")
                self.open_ai_model = self.config[matching_keywords[0]].get("open_ai_model","")
                self.prompt = self.config[matching_keywords[0]].get("prompt", "")
                openai_chat_url = self.open_ai_api_base
                openai_headers = self._get_openai_headers()
                openai_payload = None
                #all_prompt = f"{self.prompt}\n\n'''{content[len(matching_keywords[0]):]}'''"
                #print(all_prompt)
                if self.api_type == "cf-image":
                    translatorCfg = self.config.get("#translator#")
                    print(translatorCfg)
                    trans_user_prompt = Utils.translate(self,endpoint=translatorCfg.get("open_ai_api_base"),appkey=translatorCfg.get("open_ai_api_key"),query=content[len(matching_keywords[0]):],from_lang="chinese",to_lang="english")
                    print(self.prompt+" "+trans_user_prompt)
                    openai_payload = { "prompt": self.prompt+" "+trans_user_prompt}
                elif self.api_type == "openai":
                    all_prompt = f"{self.prompt}\n\n'''{content[len(matching_keywords[0]):]}'''"
                    openai_payload = self._get_openai_payload(all_prompt)
                elif self.api_type == "openai-img":
                    all_prompt = self.prompt+" "+content[len(matching_keywords[0]):]
                    openai_payload = self._get_openai_payload(all_prompt)
                logger.debug(f"[KeywordCall] openai_chat_url: {openai_chat_url}, openai_headers: {openai_headers}, openai_payload: {openai_payload}")
                response = requests.post(openai_chat_url, headers=openai_headers, json=openai_payload, timeout=60)
                response.raise_for_status()
                if self.api_type == "cf-image":
                    result = response.json()['result']['image']
                    base64Content = base64.b64decode(result)
                    b_img = io.BytesIO(base64Content)
                    reply = Reply(ReplyType.IMAGE,b_img)
                    e_context["reply"] = reply
                elif self.api_type == "openai":
                    result = response.json()['choices'][0]['message']['content']
                    if "[Generated Image]" in response.text:
                        match = re.search(r"!\[Generated Image\]\((https://[^\)]+)\)", result)
                        image_url = match.group(1)
                        reply = Reply(ReplyType.IMAGE_URL,image_url)
                    elif "[Image]" in response.text:
                        match = re.search(r"!\[Image\]\((https://[^\)]+)\)", result)
                        image_url = match.group(1)
                        reply = Reply(ReplyType.IMAGE_URL,image_url)
                    else:
                        reply = Reply(ReplyType.TEXT, result)
                    e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                return

        except Exception as e:
            if retry_count < 3:
                logger.warning(f"[KeywordCall] {str(e)}, retry {retry_count + 1}")
                self.on_handle_context(e_context, retry_count + 1)
                return

            logger.exception(f"[KeywordCall] {str(e)}")
            reply = Reply(ReplyType.ERROR, self.error_reply)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

    def get_help_text(self, verbose, **kwargs):
        return f'根据设定的关键字调用相应的API服务'

    def _load_config_template(self):
        logger.debug("No KeywordCall plugin config.json, use plugins/keyword_call/config.json.template")
        try:
            plugin_config_path = os.path.join(self.path, "config.json.template")
            if os.path.exists(plugin_config_path):
                with open(plugin_config_path, "r", encoding="utf-8") as f:
                    plugin_conf = json.load(f)
                    return plugin_conf
        except Exception as e:
            logger.exception(e)

    def _get_openai_headers(self):
        return {
            'Authorization': f"Bearer {self.open_ai_api_key}",
            'Host': urlparse(self.open_ai_api_base).netloc
        }

    def _get_openai_payload(self, content):
        messages = [{"role": "user", "content": content}]
        payload = {
            'model': self.open_ai_model,
            'messages': messages
        }
        return payload
