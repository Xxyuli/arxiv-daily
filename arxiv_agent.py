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
import fitz  # 
import glob

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
    # --- 新增字段 ---
    full_text: Optional[str] = None      # 论文正文
    main_figure_path: Optional[str] = None  # 模型主图路径
    main_table_path: Optional[str] = None   # 主实验表路径


class ArxivAgent:
    """arXiv论文监控Agent"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """初始化Agent"""
        self.config = self._load_config(config_path)
        self._setup_ai_client()
        self.pdf_dir = "pdfs"
        self.figure_dir = "figures"
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.figure_dir, exist_ok=True)
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
        elif provider == "qwen":
            qwen_config = self.config['ai_model']['qwen']
            self.ai_client = openai.OpenAI(
                api_key=os.getenv(qwen_config['api_key_env']),
                base_url=qwen_config['base_url']
            )
            self.model_name = qwen_config['model']
        elif provider == "deepseek":
            deepseek_config = self.config['ai_model']['deepseek']
            self.ai_client = openai.OpenAI(
                api_key=os.getenv(deepseek_config['api_key_env']),
                base_url=deepseek_config['base_url']
            )
            self.model_name = deepseek_config['model']
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")
        
        logger.info(f"AI客户端设置完成: {provider}")
    
    # ===== 新增方法：下载 PDF =====


    def _download_pdf(self, arxiv_id: str) -> Optional[str]:
        """下载论文PDF"""
        # 提取纯 arXiv ID（处理 oai:arXiv.org:xxxx.xxxxx 格式）
        match = re.search(r'arxiv\.org:([^/\s]+)', arxiv_id, re.IGNORECASE)
        if match:
            arxiv_id = match.group(1)
        # 如果已经是纯ID格式（如 2510.05180v1），直接使用
        # 移除版本号后缀（如 v1, v2）用于下载PDF
        clean_id = re.sub(r'v\d+$', '', arxiv_id)
        pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"
        pdf_path = os.path.join(self.pdf_dir, f"{clean_id}.pdf")
        if os.path.exists(pdf_path):
            return pdf_path
        try:
            resp = requests.get(pdf_url, timeout=30)
            if resp.status_code == 200:
                with open(pdf_path, "wb") as f:
                    f.write(resp.content)
                return pdf_path
        except Exception as e:
            logger.error(f"下载PDF失败 ({arxiv_id}): {e}")
        return None

    # ===== 新增方法：提取正文和主图/主表 =====
    def _extract_full_text_and_figures(self, paper: Paper) -> None:
        """从PDF提取正文、主图、主表"""
        
        pdf_path = self._download_pdf(paper.arxiv_id)
        if not pdf_path or not os.path.exists(pdf_path):
            logger.warning(f"无法获取PDF，跳过正文提取: {paper.arxiv_id}")
            return

        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            main_figure_path = None
            main_table_path = None

            # 提取全文（前10页足够，避免过长）
            for page_num in range(min(10, doc.page_count)):
                full_text += doc[page_num].get_text()

            # 截断至 8000 字符（防止 LLM token 超限）
            paper.full_text = full_text  #   full_text[:8000]

            # 搜索主图（架构图）和主表（结果表）
            for page_num in range(min(8, doc.page_count)):  # 通常在前8页
                page = doc[page_num]    
                text = page.get_text().lower()

                # 启发式：识别架构图
                if not main_figure_path and (
                    "architecture" in text or
                    "framework" in text or
                    "model" in text and ("figure" in text or "fig." in text)
                ):
                    images = page.get_images(full=True)
                    if images:
                        xref = images[0][0]
                        base_image = doc.extract_image(xref)
                        img_bytes = base_image["image"]
                        main_figure_path = os.path.join(self.figure_dir, f"{paper.arxiv_id}_main_fig.png")
                        with open(main_figure_path, "wb") as f:
                            f.write(img_bytes)

                # 启发式：识别主实验表
                if not main_table_path and (
                    "result" in text or
                    "performance" in text or
                    "comparison" in text
                ) and ("table" in text):
                    images = page.get_images(full=True)
                    if images:
                        xref = images[0][0]
                        base_image = doc.extract_image(xref)
                        img_bytes = base_image["image"]
                        main_table_path = os.path.join(self.figure_dir, f"{paper.arxiv_id}_main_table.png")
                        with open(main_table_path, "wb") as f:
                            f.write(img_bytes)

            paper.main_figure_path = main_figure_path
            paper.main_table_path = main_table_path
            doc.close()

        except Exception as e:
            logger.error(f"PDF解析失败 ({paper.arxiv_id}): {e}")

    def reasoning(self, context: Dict) -> str:
        # ... 保持不变 ...
        current_date = datetime.now()
        logger.info(f"当前时间: {current_date}")
        reasoning = f"""
        今天是 {current_date.strftime('%Y年%m月%d日')}，我需要：
        1. 检查arXiv上是否有新的论文发布
        2. 根据配置的关键词和分类筛选相关论文
        3. 下载论文PDF并提取正文、主图、主表
        4. 对论文正文进行AI分析
        5. 生成包含图文的Markdown报告
        6. 将报告保存到指定位置
        
        配置信息：
        - 监控分类: {', '.join(self.config['arxiv']['categories'])}
        - 关键词: {', '.join(self.config['arxiv']['keywords'])}
        - 最大论文数: {self.config['arxiv']['max_papers_per_day']}
        """
        logger.info("思考完成，制定行动计划")
        return reasoning

    def observing(self, reasoning: str) -> List[Paper]:
        # ... 原逻辑不变 ...
        logger.info("开始观察阶段 - 从arXiv获取论文...")
        papers = []
        categories = self.config['arxiv']['categories']
        keywords = self.config['arxiv']['keywords']
        max_papers = self.config['arxiv']['max_papers_per_day']
        for category in categories:
            logger.info(f"正在获取分类 {category} 的论文...")
            category_papers = self._fetch_papers_from_category(category)
            filtered_papers = self._filter_papers_by_keywords(category_papers, keywords)
            papers.extend(filtered_papers)
            if len(papers) >= max_papers:
                papers = papers[:max_papers]
                break
        seen = set()
        unique = []
        for p in papers:
            if p.arxiv_id not in seen:
                seen.add(p.arxiv_id)
                unique.append(p)
        papers = unique

        logger.info(f"观察完成，共获取到 {len(papers)} 篇相关论文")

        # === 新增：为每篇论文提取正文和图片 ===
        for paper in papers:
            self._extract_full_text_and_figures(paper)

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
        # ... 保持不变 ...
        try:
            arxiv_id = entry.id.split('/')[-1]
            authors = [author.name for author in entry.authors] if hasattr(entry, 'authors') else []
            categories = [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else []
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
        # ... 保持不变 ...
        filtered_papers = []
        for paper in papers:
            text_to_check = f"{paper.title} {paper.abstract}".lower()
            for keyword in keywords:
                if keyword.lower() in text_to_check:
                    filtered_papers.append(paper)
                    break
        return filtered_papers

    def _find_source_code_url(self, paper: Paper) -> Optional[str]:
        # ... 保持不变 ...
        try:
            github_patterns = [r'github\.com/[^/\s]+/[^/\s]+', r'https://github\.com/[^/\s]+/[^/\s]+']
            gitlab_patterns = [r'gitlab\.com/[^/\s]+/[^/\s]+', r'https://gitlab\.com/[^/\s]+/[^/\s]+']
            text_to_search = f"{paper.title} {paper.abstract}".lower()
            for pattern in github_patterns + gitlab_patterns:
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
        """使用AI分析论文正文（而非摘要）"""
        try:
            # 使用 full_text，若无则回退到 abstract
            content_to_analyze = paper.full_text if paper.full_text else paper.abstract
            # 截断避免过长
            # if len(content_to_analyze) > 6000:
            #     content_to_analyze = content_to_analyze[:6000] + "...（内容过长已截断）"

            prompt = f"""
            {self.config['ai_model']['analysis_prompt']}
            
            论文信息：
            标题：{paper.title}
            作者：{', '.join(paper.authors)}
            arXiv ID：{paper.arxiv_id}
            链接：{paper.url}
            
            论文正文（节选）：
            {content_to_analyze}
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
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return f"AI分析失败: {str(e)}"

    def _generate_markdown_report(self, papers: List[Paper]) -> str:
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
            
            # === 新增：插入主图和主表 ===
            # if paper.main_figure_path and os.path.exists(paper.main_figure_path):
            #     rel_path = os.path.relpath(paper.main_figure_path, start=os.path.dirname(self.config['output']['output_dir']))
            #     markdown += f"\n### 模型架构图\n![]({paper.main_figure_path})\n"
            
            # if paper.main_table_path and os.path.exists(paper.main_table_path):
            #     markdown += f"\n### 主要实验结果\n![]({paper.main_table_path})\n"

            if paper.abstract:
                # 可选：对摘要做简单换行处理，避免超长单行（Markdown 中段落需空行）
                abstract_clean = paper.abstract.strip().replace('\n', ' ')
                markdown += f"""
            ### 原文摘要
            {abstract_clean}
"""
            
            markdown += f"""

            
### AI分析（基于论文正文）
{paper.ai_analysis}

---

"""
        return markdown

    def _save_report(self, markdown_report: str):
        # ... 保持不变 ...
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
        # ... 保持不变 ...
        logger.info("开始运行arXiv论文监控Agent...")
        try:
            reasoning = self.reasoning({})
            papers = self.observing(reasoning)
            if not papers:
                logger.info("今日未发现相关论文")
                return
            report = self.acting(papers)
            logger.info("arXiv论文监控Agent运行完成！")

        except Exception as e:
            logger.error(f"Agent运行失败: {e}")
            raise
        finally:
            # === 新增：清理 self.pdf_dir 下所有 .pdf 文件 ===
            if hasattr(self, 'pdf_dir') and self.pdf_dir and os.path.exists(self.pdf_dir):
                try:
                    pdf_files = glob.glob(os.path.join(self.pdf_dir, "*.pdf"))
                    for pdf_file in pdf_files:
                        os.remove(pdf_file)
                        logger.debug(f"已删除临时PDF: {pdf_file}")
                    logger.info(f"已清理 {len(pdf_files)} 个PDF文件，目录: {self.pdf_dir}")
                except Exception as e:
                    logger.warning(f"清理PDF文件时出错: {e}")

if __name__ == "__main__":
    agent = ArxivAgent()
    agent.run()