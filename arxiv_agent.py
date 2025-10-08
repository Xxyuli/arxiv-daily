#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv论文监控Agent
基于React思考流程：Reasoning（思考）- Observing（观察）- Acting（执行）
"""

import os
import yaml
import logging
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import openai
import re
from urllib.parse import urljoin, urlparse

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arxiv_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Paper:
    """论文数据结构"""
    title: str
    authors: List[str]
    abstract: str
    arxiv_id: str
    url: str
    published: str
    categories: List[str]
    source_code_url: Optional[str] = None
    ai_analysis: Optional[str] = None

class ArxivAgent:
    """arXiv论文监控Agent"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """初始化Agent"""
        self.config = self._load_config(config_path)
        self._setup_ai_client()
        logger.info("arXiv Agent 初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
    
    def _setup_ai_client(self):
        """设置AI客户端"""
        provider = self.config['ai_model']['provider']
        
        if provider == "openai":
            openai_config = self.config['ai_model']['openai']
            self.ai_client = openai.OpenAI(
                api_key=os.getenv(openai_config['api_key_env']),
                base_url=openai_config['base_url']
            )
            self.model_name = openai_config['model']
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")
        
        logger.info(f"AI客户端设置完成: {provider}")
    
    def reasoning(self, context: Dict) -> str:
        """
        Reasoning（思考）阶段
        分析当前情况并制定行动计划
        """
        logger.info("开始思考阶段...")
        
        # 分析当前日期和时间
        current_date = datetime.now()
        logger.info(f"当前时间: {current_date}")
        
        # 思考今天需要做什么
        reasoning = f"""
        今天是 {current_date.strftime('%Y年%m月%d日')}，我需要：
        1. 检查arXiv上是否有新的论文发布
        2. 根据配置的关键词和分类筛选相关论文
        3. 对筛选出的论文进行AI分析
        4. 生成Markdown格式的报告
        5. 将报告保存到指定位置
        
        配置信息：
        - 监控分类: {', '.join(self.config['arxiv']['categories'])}
        - 关键词: {', '.join(self.config['arxiv']['keywords'])}
        - 最大论文数: {self.config['arxiv']['max_papers_per_day']}
        """
        
        logger.info("思考完成，制定行动计划")
        return reasoning
    
    def observing(self, reasoning: str) -> List[Paper]:
        """
        Observing（观察）阶段
        从arXiv获取最新论文信息
        """
        logger.info("开始观察阶段 - 从arXiv获取论文...")
        
        papers = []
        categories = self.config['arxiv']['categories']
        keywords = self.config['arxiv']['keywords']
        max_papers = self.config['arxiv']['max_papers_per_day']
        
        for category in categories:
            logger.info(f"正在获取分类 {category} 的论文...")
            category_papers = self._fetch_papers_from_category(category)
            
            # 根据关键词过滤
            filtered_papers = self._filter_papers_by_keywords(category_papers, keywords)
            papers.extend(filtered_papers)
            
            if len(papers) >= max_papers:
                papers = papers[:max_papers]
                break
        
        logger.info(f"观察完成，共获取到 {len(papers)} 篇相关论文")
        return papers
    
    def _fetch_papers_from_category(self, category: str) -> List[Paper]:
        """从指定分类获取论文"""
        # arXiv RSS feed URL
        url = f"http://arxiv.org/rss/{category}"
        
        try:
            feed = feedparser.parse(url)
            papers = []
            
            for entry in feed.entries:
                paper = self._parse_paper_entry(entry)
                if paper:
                    papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"获取分类 {category} 的论文失败: {e}")
            return []
    
    def _parse_paper_entry(self, entry) -> Optional[Paper]:
        """解析论文条目"""
        try:
            # 提取arXiv ID
            arxiv_id = entry.id.split('/')[-1]
            
            # 提取作者信息
            authors = []
            if hasattr(entry, 'authors'):
                authors = [author.name for author in entry.authors]
            
            # 提取分类
            categories = []
            if hasattr(entry, 'tags'):
                categories = [tag.term for tag in entry.tags]
            
            paper = Paper(
                title=entry.title,
                authors=authors,
                abstract=entry.summary,
                arxiv_id=arxiv_id,
                url=entry.link,
                published=entry.published,
                categories=categories
            )
            
            return paper
            
        except Exception as e:
            logger.error(f"解析论文条目失败: {e}")
            return None
    
    def _filter_papers_by_keywords(self, papers: List[Paper], keywords: List[str]) -> List[Paper]:
        """根据关键词过滤论文"""
        filtered_papers = []
        
        for paper in papers:
            # 检查标题和摘要是否包含关键词
            text_to_check = f"{paper.title} {paper.abstract}".lower()
            
            for keyword in keywords:
                if keyword.lower() in text_to_check:
                    filtered_papers.append(paper)
                    break
        
        return filtered_papers
    
    def _find_source_code_url(self, paper: Paper) -> Optional[str]:
        """
        尝试从论文中提取源码链接
        这里实现一个简单的启发式方法
        """
        try:
            # 常见的源码托管平台
            github_patterns = [
                r'github\.com/[^/\s]+/[^/\s]+',
                r'https://github\.com/[^/\s]+/[^/\s]+',
            ]
            
            gitlab_patterns = [
                r'gitlab\.com/[^/\s]+/[^/\s]+',
                r'https://gitlab\.com/[^/\s]+/[^/\s]+',
            ]
            
            text_to_search = f"{paper.title} {paper.abstract}".lower()
            
            # 搜索GitHub链接
            for pattern in github_patterns:
                match = re.search(pattern, text_to_search, re.IGNORECASE)
                if match:
                    url = match.group(0)
                    if not url.startswith('http'):
                        url = 'https://' + url
                    return url
            
            # 搜索GitLab链接
            for pattern in gitlab_patterns:
                match = re.search(pattern, text_to_search, re.IGNORECASE)
                if match:
                    url = match.group(0)
                    if not url.startswith('http'):
                        url = 'https://' + url
                    return url
            
            return None
            
        except Exception as e:
            logger.error(f"搜索源码链接失败: {e}")
            return None
    
    def acting(self, papers: List[Paper]) -> str:
        """
        Acting（执行）阶段
        对论文进行AI分析并生成报告
        """
        logger.info("开始执行阶段 - 进行AI分析...")
        
        # 为每篇论文添加源码链接和AI分析
        for i, paper in enumerate(papers):
            logger.info(f"正在分析论文 {i+1}/{len(papers)}: {paper.title[:50]}...")
            
            # 查找源码链接
            paper.source_code_url = self._find_source_code_url(paper)
            
            # AI分析
            paper.ai_analysis = self._analyze_paper_with_ai(paper)
        
        # 生成Markdown报告
        markdown_report = self._generate_markdown_report(papers)
        
        # 保存报告
        self._save_report(markdown_report)
        
        logger.info("执行阶段完成，报告已生成并保存")
        return markdown_report
    
    def _analyze_paper_with_ai(self, paper: Paper) -> str:
        """使用AI分析论文"""
        try:
            prompt = f"""
            {self.config['ai_model']['analysis_prompt']}
            
            论文信息：
            标题：{paper.title}
            作者：{', '.join(paper.authors)}
            摘要：{paper.abstract}
            arXiv ID：{paper.arxiv_id}
            链接：{paper.url}
            """
            
            response = self.ai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI研究分析师，擅长分析学术论文。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            return analysis
            
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return f"AI分析失败: {str(e)}"
    
    def _generate_markdown_report(self, papers: List[Paper]) -> str:
        """生成Markdown格式的报告"""
        current_date = datetime.now()
        date_str = current_date.strftime("%Y年%m月%d日")
        
        markdown = f"""# arXiv论文监控报告 - {date_str}

> 本报告由arXiv论文监控Agent自动生成

## 报告概览

- **监控日期**: {date_str}
- **监控分类**: {', '.join(self.config['arxiv']['categories'])}
- **关键词**: {', '.join(self.config['arxiv']['keywords'])}
- **发现论文数**: {len(papers)}篇

---

"""
        
        for i, paper in enumerate(papers, 1):
            markdown += f"""## {i}. {paper.title}

### 基本信息
- **作者**: {', '.join(paper.authors) if paper.authors else '未知'}
- **arXiv ID**: [{paper.arxiv_id}]({paper.url})
- **发布日期**: {paper.published}
- **分类**: {', '.join(paper.categories) if paper.categories else '未知'}
- **论文链接**: [arXiv链接]({paper.url})
"""
            
            if paper.source_code_url:
                markdown += f"- **源码地址**: [查看源码]({paper.source_code_url})\n"
            
            markdown += f"""
### 摘要
{paper.abstract}

### AI分析
{paper.ai_analysis}

---

"""
        
        return markdown
    
    def _save_report(self, markdown_report: str):
        """保存报告到文件"""
        try:
            output_dir = self.config['output']['output_dir']
            os.makedirs(output_dir, exist_ok=True)
            
            current_date = datetime.now()
            filename_format = self.config['output']['filename_format']
            filename = current_date.strftime(filename_format.replace('{date}', '%Y-%m-%d'))
            
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            
            logger.info(f"报告已保存到: {filepath}")
            
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            raise
    
    def run(self):
        """运行完整的React流程"""
        logger.info("开始运行arXiv论文监控Agent...")
        
        try:
            # Reasoning: 思考阶段
            reasoning = self.reasoning({})
            
            # Observing: 观察阶段
            papers = self.observing(reasoning)
            
            if not papers:
                logger.info("今日未发现相关论文")
                return
            
            # Acting: 执行阶段
            report = self.acting(papers)
            
            logger.info("arXiv论文监控Agent运行完成！")
            
        except Exception as e:
            logger.error(f"Agent运行失败: {e}")
            raise

if __name__ == "__main__":
    agent = ArxivAgent()
    agent.run()

