import os
from openai import AsyncOpenAI
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentSummarizer:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")  # 新增：支持自定义API地址
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        # 配置客户端
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base if api_base else None  # 如果设置了自定义地址就使用它
        )

    async def summarize(self, contents: List[Dict], description: str) -> str:
        """
        使用OpenAI API总结多个网页的内容
        """
        try:
            # 准备提示词
            prompt = self._prepare_prompt(contents, description)
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),  # 新增：支持自定义模型
                messages=[
                    {"role": "system", "content": "你是一个专业的网页内容分析助手。请根据用户的要求，分析并总结提供的网页内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=True  # 启用流式模式
            )
            
            # 收集流式响应
            full_response = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            return full_response
            
        except Exception as e:
            logger.error(f"Error summarizing content: {str(e)}")
            raise

    def _prepare_prompt(self, contents: List[Dict], description: str) -> str:
        """
        准备发送给OpenAI的提示词
        """
        prompt = f"用户要求：{description}\n\n以下是需要分析的网页内容：\n\n"
        
        for i, content in enumerate(contents, 1):
            prompt += f"网页 {i}:\n"
            prompt += f"标题：{content['title']}\n"
            if content['meta_description']:
                prompt += f"描述：{content['meta_description']}\n"
            prompt += f"内容：{content['content']}\n\n"
        
        prompt += "请根据用户的要求，对以上内容进行分析和总结。总结应该包括：\n"
        prompt += "1. 主要内容概述\n"
        prompt += "2. 关键信息提取\n"
        prompt += "3. 与用户要求相关的具体分析\n"
        prompt += "4. 总结和建议\n"
        
        return prompt 