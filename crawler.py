import aiohttp
from bs4 import BeautifulSoup
import asyncio
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def crawl(self, url: str) -> dict:
        """
        异步爬取网页内容
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch {url}: HTTP {response.status}")
                    
                    html = await response.text()
                    return self._parse_content(html, url)
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            raise

    def _parse_content(self, html: str, url: str) -> dict:
        """
        解析网页内容，提取标题、正文等
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除不需要的元素
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # 提取标题
        title = soup.title.string if soup.title else ""
        
        # 提取正文内容
        content = ""
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:
                content += text + "\n"
        
        # 提取元数据
        meta_description = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            meta_description = meta_tag.get('content', '')
        
        return {
            'url': url,
            'title': title,
            'content': content.strip(),
            'meta_description': meta_description
        } 