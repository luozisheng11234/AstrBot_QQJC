from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import httpx
from typing import Optional, Dict, Any


@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_all_message(self, event: AstrMessageEvent):
        获取用户发送的消息 = event.message_str
        if 获取用户发送的消息 is not None:
            async with FeishuWebhook("https://open.feishu.cn/open-apis/bot/v2/hook/ac945fce-3ebd-4e8e-95d5-6c25d6bf8191") as webhook:
                await webhook.发送富文本信息(
                        f"群聊ID: {获取QQ群}",
                        f"发送者QQ名称: {获取用户的QQ名称}, \n 发送信息: {获取用户发送的消息}"
                    )
            #yield event.plain_result("收到了一条消息。")
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("QQ")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        获取用户的QQ名称 = event.message_obj.sender.nickname
        获取用户发送的消息 = event.message_str # 用户发的纯文本消息字符串
        获取QQ群 = event.message_obj.group_id
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 测试一下 {message_str}!, 群聊ID: {获取QQ群}, 发送者QQ名称: {获取用户的QQ名称}, 发送者QQID: {获取用户发送的消息}") # 发送一条纯文本消息


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""




class FeishuWebhook:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.client = None
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            
    async def 发送文本信息(self, text: str) -> Optional[Dict[str, Any]]:
        """发送文本消息"""
        payload = {
            "msg_type": "text",
            "content": {"text": text}
        }
        
        try:
            response = await self.client.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP错误: {e.response.status_code}")
        except Exception as e:
            print(f"发送消息失败: {e}")
        return None
    
    async def 发送富文本信息(self, title: str, content: str, 颜色: str = "blue") -> Optional[Dict[str, Any]]:
        """发送markdown消息"""
        payload = {
                "msg_type": "interactive",
                "card": {
                    "schema": "2.0",
                    "config": {
                        "update_multi": True,
                        "style": {
                            "text_size": {
                                "normal_v2": {
                                    "default": "normal",
                                    "pc": "normal",
                                    "mobile": "heading",
                                }
                            }
                        },
                    },
                    "body": {
                        "direction": "vertical",
                        "padding": "12px 12px 12px 12px",
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": f"""<font color='{颜色}'>{content}</font>""",
                                "text_align": "left",
                                "text_size": "normal_v2",
                                "margin": "0px 0px 0px 0px",
                            },
                        ],
                    },
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": title,
                        },
                        "subtitle": {
                            "tag": "plain_text",
                            "content": "",
                        },
                        "template": "blue",
                        "padding": "12px 12px 12px 12px",
                    },
                },
            }
        
        
        try:
            response = await self.client.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"发送markdown消息失败: {e}")
        return None



