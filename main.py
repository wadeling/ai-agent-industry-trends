from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from typing import List
import os
from dotenv import load_dotenv

from crawler import WebCrawler
from summarizer import ContentSummarizer

# 加载环境变量
load_dotenv()

app = FastAPI(title="AI Web Content Analyzer")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板目录
templates = Jinja2Templates(directory="templates")

# 初始化爬虫和总结器
crawler = WebCrawler()
summarizer = ContentSummarizer()

class CrawlRequest(BaseModel):
    urls: List[str]
    description: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>AI Web Content Analyzer</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                textarea { width: 100%; height: 100px; margin: 10px 0; }
                input[type="text"] { width: 100%; padding: 5px; margin: 5px 0; }
                button { padding: 10px 20px; background-color: #007bff; color: white; border: none; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI Web Content Analyzer</h1>
                <form id="crawlForm">
                    <div>
                        <label for="urls">URLs (每行一个):</label>
                        <textarea id="urls" name="urls" required></textarea>
                    </div>
                    <div>
                        <label for="description">描述您想要分析的内容:</label>
                        <textarea id="description" name="description" required></textarea>
                    </div>
                    <button type="submit">分析</button>
                </form>
                <div id="result"></div>
            </div>
            <script>
                document.getElementById('crawlForm').onsubmit = async (e) => {
                    e.preventDefault();
                    const urls = document.getElementById('urls').value.split('\\n').filter(url => url.trim());
                    const description = document.getElementById('description').value;
                    
                    try {
                        const response = await fetch('/api/analyze', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ urls, description })
                        });
                        const data = await response.json();
                        document.getElementById('result').innerHTML = data.summary;
                    } catch (error) {
                        document.getElementById('result').innerHTML = 'Error: ' + error.message;
                    }
                };
            </script>
        </body>
    </html>
    """

@app.post("/api/analyze")
async def analyze_content(request: CrawlRequest):
    try:
        # 爬取网页内容
        contents = []
        for url in request.urls:
            content = await crawler.crawl(url)
            contents.append(content)
        
        # 使用大语言模型总结内容
        summary = await summarizer.summarize(contents, request.description)
        
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 