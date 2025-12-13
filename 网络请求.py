import httpx
import asyncio
from typing import Optional, Dict, Any

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
    
    async def 发送富文本信息(self, title: str, content: str) -> Optional[Dict[str, Any]]:
        """发送markdown消息"""
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    }
                },
                "elements": [{
                    "tag": "markdown",
                    "content": content
                }]
            }
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

# 使用示例
async def example_usage():
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/ac945fce-3ebd-4e8e-95d5-6c25d6bf8191"
    
    async with FeishuWebhook(webhook_url) as feishu:
        # 发送文本消息
        result = await feishu.发送文本信息("Hello from async httpx!")
        if result:
            print(f"消息发送成功: {result}")
        
        # 发送markdown消息
        md_result = await feishu.发送富文本信息(
            title="异步通知",
            content="**这是来自异步客户端的消息**\n\n- 项目：测试\n- 状态：成功"
        )

