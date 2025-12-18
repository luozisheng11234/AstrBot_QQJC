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
        获取QQ群 = event.message_obj.group_id
        获取用户的QQ名称 = event.message_obj.sender.nickname
        if 获取用户发送的消息 is not None and 获取用户发送的消息 != "" and "弘升" in 获取用户的QQ名称:
            async with FeishuWebhook("https://open.feishu.cn/open-apis/bot/v2/hook/2ef23e46-ba4e-4830-bff7-50cc8629e33c") as webhook:
                await webhook.发送富文本信息(
                        f"群聊ID: {获取QQ群}",
                        f"发送者QQ名称: {获取用户的QQ名称}, \n 发送信息: {获取用户发送的消息}"
                    )
        if 获取用户发送的消息 is not None and 获取用户发送的消息 != "" and "罗梓晟" in 获取用户的QQ名称:
            信息ID = event.message_obj.message_id
            获取QQ群 = event.message_obj.group_id
            payload = {
                    "group_id": 获取QQ群,
                    "message": [
                        {
                            "type": "reply",
                            "data": {
                                "id": 信息ID
                            }
                        },
                        {
                            "type": "text",
                            "data": {
                                "text": "回复你了"
                            }
                        }
                    ]
            }
            ret = await self.QQapi(event, "send_group_msg", payload)
            logger.info(ret)
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

    @filter.command("QC")
    async def QC(self, event: AstrMessageEvent):
        ret = await self.QQapi(event, "get_status", {})
        yield event.plain_result(f"Hello, {ret}") # 发送一条纯文本消息

    async def QQapi(self, event: AstrMessageEvent, api_name: str, payloads: Dict[str, Any]):
        if event.get_platform_name() == "aiocqhttp":
            # qq
            from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
            assert isinstance(event, AiocqhttpMessageEvent)
            client = event.bot # 得到 client
            ret = await client.api.call_action(api_name, **payloads) # 调用 协议端  API
            return ret
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



