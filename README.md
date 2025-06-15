# AI Web Content Analyzer

这是一个基于Python的AI Agent，可以爬取网页内容并使用大语言模型进行智能分析和总结。

## 功能特点

- 支持多网页内容爬取
- 使用OpenAI GPT模型进行内容分析和总结
- 提供简洁的Web界面
- RESTful API接口
- 异步处理提高性能

## 安装要求

- Python 3.8+
- OpenAI API密钥

## 安装步骤

1. 克隆项目到本地：
```bash
git clone [repository_url]
cd [project_directory]
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并添加以下内容：
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 运行项目

```bash
python main.py
```

服务将在 http://localhost:8000 启动

## API使用

### 分析网页内容

POST `/api/analyze`

请求体示例：
```json
{
    "urls": [
        "https://example.com/page1",
        "https://example.com/page2"
    ],
    "description": "分析这些网页中关于AI技术的最新发展"
}
```

## 注意事项

- 请确保您有有效的OpenAI API密钥
- 建议在使用前先测试单个网页的爬取
- 注意遵守目标网站的robots.txt规则
- 建议适当控制请求频率，避免对目标网站造成压力