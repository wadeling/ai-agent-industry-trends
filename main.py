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
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.css">
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px;
                    background-color: #f5f5f5;
                }
                .container { 
                    max-width: 1000px; 
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                textarea { 
                    width: 100%; 
                    height: 100px; 
                    margin: 10px 0;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    resize: vertical;
                }
                input[type="text"] { 
                    width: 100%; 
                    padding: 10px;
                    margin: 5px 0;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                button { 
                    padding: 12px 24px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: background-color 0.2s;
                }
                button:hover {
                    background-color: #0056b3;
                }
                #result {
                    margin-top: 20px;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: white;
                }
                .loading {
                    display: none;
                    margin-top: 20px;
                    text-align: center;
                    color: #666;
                }
                .loading::after {
                    content: "...";
                    animation: dots 1.5s steps(5, end) infinite;
                }
                @keyframes dots {
                    0%, 20% { content: "."; }
                    40% { content: ".."; }
                    60% { content: "..."; }
                    80%, 100% { content: ""; }
                }
                .markdown-body {
                    padding: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI Web Content Analyzer</h1>
                <form id="crawlForm">
                    <div>
                        <label for="urls">URLs (每行一个):</label>
                        <textarea id="urls" name="urls" required placeholder="https://example.com/page1&#10;https://example.com/page2"></textarea>
                    </div>
                    <div>
                        <label for="description">描述您想要分析的内容:</label>
                        <textarea id="description" name="description" required placeholder="请分析这些网页中关于AI技术的最新发展..."></textarea>
                    </div>
                    <button type="submit">分析</button>
                </form>
                <div class="loading" id="loading">正在分析中</div>
                <div id="result" class="markdown-body"></div>
            </div>
            <script>
                document.getElementById('crawlForm').onsubmit = async (e) => {
                    e.preventDefault();
                    const urls = document.getElementById('urls').value.split('\\n').filter(url => url.trim());
                    const description = document.getElementById('description').value;
                    const resultDiv = document.getElementById('result');
                    const loadingDiv = document.getElementById('loading');
                    
                    try {
                        loadingDiv.style.display = 'block';
                        resultDiv.innerHTML = '';
                        
                        const response = await fetch('/api/analyze', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ urls, description })
                        });
                        
                        const data = await response.json();
                        resultDiv.innerHTML = marked.parse(data.summary);
                    } catch (error) {
                        resultDiv.innerHTML = `<div style="color: red;">Error: ${error.message}</div>`;
                    } finally {
                        loadingDiv.style.display = 'none';
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