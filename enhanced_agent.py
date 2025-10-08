#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版arXiv论文监控Agent
支持多种AI提供商和高级功能
"""

import os
import yaml
import logging
import feedparser
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from dataclasses import dataclass, asdict
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
        logging.FileHandler('enhanced_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Paper:
    """增强版论文数据结构"""
    title: str
    authors: List[str]
    abstract: str
    arxiv_id: str
    url: str
    published: str
    categories: List[str]
    source_code_url: Optional[str] = None
    ai_analysis: Optional[str] = None
    relevance_score: Optional[float] = None
    key_insights: Optional[List[str]] = None
    
    def to_dict(self):
        """转换为字典格式"""
        return asdict(self)

class EnhancedArxivAgent:
    """增强版arXiv论文监控Agent"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """初始化Agent"""
        self.config = self._load_config(config_path)
        self._setup_ai_client()
        self._setup_github_client()
        logger.info("增强版arXiv Agent 初始化完成")
    
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
            self._setup_openai_client()
        elif provider == "anthropic":
            self._setup_anthropic_client()
        elif provider == "custom":
            self._setup_custom_client()
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")
        
        logger.info(f"AI客户端设置完成: {provider}")
    
    def _setup_openai_client(self):
        """设置OpenAI客户端"""
        openai_config = self.config['ai_model']['openai']
        self.ai_client = openai.OpenAI(
            api_key=os.getenv(openai_config['api_key_env']),
            base_url=openai_config['base_url']
        )
        self.model_name = openai_config['model']
        self.provider = "openai"
    
    def _setup_anthropic_client(self):
        """设置Anthropic客户端"""
        try:
            import anthropic
            anthropic_config = self.config['ai_model']['anthropic']
            self.ai_client = anthropic.Anthropic(
                api_key=os.getenv(anthropic_config['api_key_env'])
            )
            self.model_name = anthropic_config['model']
            self.provider = "anthropic"
        except ImportError:
            logger.error("Anthropic库未安装，请运行: pip install anthropic")
            raise
    
    def _setup_custom_client(self):
        """设置自定义API客户端"""
        self.custom_api_url = self.config['ai_model']['custom']['api_url']
        self.custom_api_key = os.getenv(self.config['ai_model']['custom']['api_key_env'])
        self.model_name = self.config['ai_model']['custom']['model']
        self.provider = "custom"
    
    def _setup_github_client(self):
        """设置GitHub客户端（如果需要）"""
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            try:
                from github import Github
                self.github_client = Github(github_token)
                logger.info("GitHub客户端设置完成")
            except ImportError:
                logger.warning("PyGithub库未安装，GitHub功能将不可用")
                self.github_client = None
        else:
            self.github_client = None
    
    def reasoning(self, context: Dict) -> Dict:
        """
        增强版思考阶段
        返回更详细的分析结果
        """
        logger.info("开始增强思考阶段...")
        
        current_date = datetime.now()
        yesterday = current_date - timedelta(days=1)
        
        reasoning_result = {
            "current_date": current_date.isoformat(),
            "yesterday_date": yesterday.isoformat(),
            "monitoring_categories": self.config['arxiv']['categories'],
            "keywords": self.config['arxiv']['keywords'],
            "max_papers": self.config['arxiv']['max_papers_per_day'],
            "ai_provider": self.config['ai_model']['provider'],
            "analysis_plan": [
                "1. 获取arXiv最新论文",
                "2. 关键词过滤和相关性评分",
                "3. 提取源码链接",
                "4. AI深度分析",
                "5. 生成结构化报告",
                "6. 保存并提交到GitHub"
            ]
        }
        
        logger.info("增强思考完成")
        return reasoning_result
    
    def observing(self, reasoning: Dict) -> List[Paper]:
        """
        增强版观察阶段
        支持更智能的论文筛选和评分
        """
        logger.info("开始增强观察阶段...")
        
        papers = []
        categories = self.config['arxiv']['categories']
        keywords = self.config['arxiv']['keywords']
        max_papers = self.config['arxiv']['max_papers_per_day']
        
        for category in categories:
            logger.info(f"正在获取分类 {category} 的论文...")
            category_papers = self._fetch_papers_from_category(category)
            
            # 增强版过滤和评分
            filtered_papers = self._enhanced_filter_papers(category_papers, keywords)
            papers.extend(filtered_papers)
            
            if len(papers) >= max_papers:
                papers = papers[:max_papers]
                break
        
        # 按相关性评分排序
        papers.sort(key=lambda x: x.relevance_score or 0, reverse=True)
        
        logger.info(f"增强观察完成，共获取到 {len(papers)} 篇相关论文")
        return papers
    
    def _enhanced_filter_papers(self, papers: List[Paper], keywords: List[str]) -> List[Paper]:
        """增强版论文过滤，包含相关性评分"""
        filtered_papers = []
        
        for paper in papers:
            # 计算相关性评分
            relevance_score = self._calculate_relevance_score(paper, keywords)
            
            if relevance_score > 0.3:  # 相关性阈值
                paper.relevance_score = relevance_score
                filtered_papers.append(paper)
        
        return filtered_papers
    
    def _calculate_relevance_score(self, paper: Paper, keywords: List[str]) -> float:
        """计算论文相关性评分"""
        text_to_analyze = f"{paper.title} {paper.abstract}".lower()
        
        score = 0.0
        
        # 标题匹配权重更高
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in paper.title.lower():
                score += 0.5  # 标题匹配
            if keyword_lower in paper.abstract.lower():
                score += 0.3  # 摘要匹配
        
        # 归一化评分
        max_possible_score = len(keywords) * 0.5
        normalized_score = min(score / max_possible_score, 1.0)
        
        return normalized_score
    
    def acting(self, papers: List[Paper]) -> Dict:
        """
        增强版执行阶段
        包含更详细的AI分析和结构化输出
        """
        logger.info("开始增强执行阶段...")
        
        analysis_results = {
            "total_papers": len(papers),
            "analysis_timestamp": datetime.now().isoformat(),
            "papers_analyzed": []
        }
        
        for i, paper in enumerate(papers):
            logger.info(f"正在深度分析论文 {i+1}/{len(papers)}: {paper.title[:50]}...")
            
            # 增强版源码搜索
            paper.source_code_url = self._enhanced_source_code_search(paper)
            
            # 增强版AI分析
            analysis_result = self._enhanced_ai_analysis(paper)
            paper.ai_analysis = analysis_result.get('analysis', '')
            paper.key_insights = analysis_result.get('insights', [])
            
            analysis_results["papers_analyzed"].append(paper.to_dict())
        
        # 生成增强版报告
        enhanced_report = self._generate_enhanced_report(papers)
        
        # 保存报告和元数据
        self._save_enhanced_output(enhanced_report, analysis_results)
        
        logger.info("增强执行阶段完成")
        return analysis_results
    
    def _enhanced_source_code_search(self, paper: Paper) -> Optional[str]:
        """增强版源码链接搜索"""
        search_patterns = [
            # GitHub
            r'github\.com/([^/\s]+/[^/\s]+)',
            r'https://github\.com/([^/\s]+/[^/\s]+)',
            # GitLab
            r'gitlab\.com/([^/\s]+/[^/\s]+)',
            r'https://gitlab\.com/([^/\s]+/[^/\s]+)',
            # Bitbucket
            r'bitbucket\.org/([^/\s]+/[^/\s]+)',
            # 其他常见模式
            r'code\.([^/\s]+\.com)/([^/\s]+/[^/\s]+)',
        ]
        
        text_to_search = f"{paper.title} {paper.abstract}"
        
        for pattern in search_patterns:
            matches = re.finditer(pattern, text_to_search, re.IGNORECASE)
            for match in matches:
                url = match.group(0)
                if not url.startswith('http'):
                    url = 'https://' + url
                return url
        
        return None
    
    def _enhanced_ai_analysis(self, paper: Paper) -> Dict:
        """增强版AI分析"""
        try:
            if self.provider == "openai":
                return self._openai_analysis(paper)
            elif self.provider == "anthropic":
                return self._anthropic_analysis(paper)
            elif self.provider == "custom":
                return self._custom_analysis(paper)
            else:
                raise ValueError(f"不支持的AI提供商: {self.provider}")
                
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return {
                "analysis": f"AI分析失败: {str(e)}",
                "insights": []
            }
    
    def _openai_analysis(self, paper: Paper) -> Dict:
        """OpenAI分析"""
        system_prompt = """你是一个专业的AI研究分析师。请对论文进行深度分析，并提取关键洞察。
        
        请按以下格式返回JSON：
        {
            "analysis": "详细的分析内容",
            "insights": ["洞察1", "洞察2", "洞察3"]
        }"""
        
        user_prompt = f"""
        请分析以下arXiv论文：
        
        标题：{paper.title}
        作者：{', '.join(paper.authors)}
        摘要：{paper.abstract}
        arXiv ID：{paper.arxiv_id}
        
        请提供：
        1. 核心贡献和创新点
        2. 技术方法的优缺点
        3. 实验结果分析
        4. 对领域发展的意义
        5. 潜在应用场景
        6. 改进建议
        
        同时提取3-5个关键洞察。
        """
        
        response = self.ai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2500,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
        try:
            # 尝试解析JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # 如果不是JSON格式，返回默认结构
            return {
                "analysis": content,
                "insights": self._extract_insights_from_text(content)
            }
    
    def _anthropic_analysis(self, paper: Paper) -> Dict:
        """Anthropic分析"""
        prompt = f"""
        请对以下arXiv论文进行深度分析：
        
        标题：{paper.title}
        作者：{', '.join(paper.authors)}
        摘要：{paper.abstract}
        arXiv ID：{paper.arxiv_id}
        
        请提供详细分析并提取关键洞察。
        """
        
        response = self.ai_client.messages.create(
            model=self.model_name,
            max_tokens=2500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        
        return {
            "analysis": content,
            "insights": self._extract_insights_from_text(content)
        }
    
    def _custom_analysis(self, paper: Paper) -> Dict:
        """自定义API分析"""
        headers = {
            "Authorization": f"Bearer {self.custom_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": f"请分析以下论文：{paper.title}\n\n摘要：{paper.abstract}"
                }
            ]
        }
        
        response = requests.post(self.custom_api_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        return {
            "analysis": content,
            "insights": self._extract_insights_from_text(content)
        }
    
    def _extract_insights_from_text(self, text: str) -> List[str]:
        """从文本中提取关键洞察"""
        # 简单的启发式方法提取洞察
        sentences = text.split('。')
        insights = []
        
        insight_keywords = ['创新', '突破', '改进', '优化', '新方法', '重要', '关键']
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in insight_keywords):
                if len(sentence.strip()) > 10:
                    insights.append(sentence.strip())
                    if len(insights) >= 5:
                        break
        
        return insights[:5]  # 最多5个洞察
    
    def _generate_enhanced_report(self, papers: List[Paper]) -> str:
        """生成增强版Markdown报告"""
        current_date = datetime.now()
        date_str = current_date.strftime("%Y年%m月%d日")
        
        # 统计信息
        total_papers = len(papers)
        avg_relevance = sum(p.relevance_score or 0 for p in papers) / total_papers if papers else 0
        papers_with_code = sum(1 for p in papers if p.source_code_url)
        
        markdown = f"""# arXiv论文监控报告 - {date_str}

> 本报告由增强版arXiv论文监控Agent自动生成

## 📊 报告概览

| 项目 | 数值 |
|------|------|
| **监控日期** | {date_str} |
| **发现论文数** | {total_papers}篇 |
| **平均相关性评分** | {avg_relevance:.2f} |
| **包含源码的论文** | {papers_with_code}篇 |
| **监控分类** | {', '.join(self.config['arxiv']['categories'])} |
| **关键词** | {', '.join(self.config['arxiv']['keywords'])} |

---

"""
        
        for i, paper in enumerate(papers, 1):
            relevance_badge = f"🔥 相关性: {paper.relevance_score:.2f}" if paper.relevance_score else ""
            
            markdown += f"""## {i}. {paper.title} {relevance_badge}

### 📋 基本信息
- **作者**: {', '.join(paper.authors) if paper.authors else '未知'}
- **arXiv ID**: [`{paper.arxiv_id}`]({paper.url})
- **发布日期**: {paper.published}
- **分类**: {', '.join(paper.categories) if paper.categories else '未知'}
- **论文链接**: [🔗 arXiv链接]({paper.url})
"""
            
            if paper.source_code_url:
                markdown += f"- **源码地址**: [💻 查看源码]({paper.source_code_url})\n"
            
            markdown += f"""
### 📝 摘要
{paper.abstract}

### 🤖 AI分析
{paper.ai_analysis}

### 💡 关键洞察
"""
            
            if paper.key_insights:
                for insight in paper.key_insights:
                    markdown += f"- {insight}\n"
            else:
                markdown += "- 暂无关键洞察\n"
            
            markdown += "\n---\n\n"
        
        # 添加总结部分
        markdown += f"""## 📈 今日总结

今日共监控到 {total_papers} 篇相关论文，平均相关性评分为 {avg_relevance:.2f}。
其中有 {papers_with_code} 篇论文提供了源码链接，便于进一步研究。

### 🎯 重点关注
"""
        
        # 推荐最相关的论文
        top_papers = sorted(papers, key=lambda x: x.relevance_score or 0, reverse=True)[:3]
        for i, paper in enumerate(top_papers, 1):
            markdown += f"{i}. [{paper.title}]({paper.url}) (相关性: {paper.relevance_score:.2f})\n"
        
        return markdown
    
    def _save_enhanced_output(self, markdown_report: str, analysis_results: Dict):
        """保存增强版输出"""
        try:
            output_dir = self.config['output']['output_dir']
            os.makedirs(output_dir, exist_ok=True)
            
            current_date = datetime.now()
            date_str = current_date.strftime("%Y-%m-%d")
            
            # 保存Markdown报告
            md_filename = f"{date_str}_enhanced_papers.md"
            md_filepath = os.path.join(output_dir, md_filename)
            
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            
            # 保存JSON元数据
            json_filename = f"{date_str}_analysis_metadata.json"
            json_filepath = os.path.join(output_dir, json_filename)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"增强版报告已保存到: {md_filepath}")
            logger.info(f"分析元数据已保存到: {json_filepath}")
            
        except Exception as e:
            logger.error(f"保存增强版输出失败: {e}")
            raise
    
    def run(self):
        """运行增强版React流程"""
        logger.info("开始运行增强版arXiv论文监控Agent...")
        
        try:
            # Reasoning: 增强思考阶段
            reasoning = self.reasoning({})
            
            # Observing: 增强观察阶段
            papers = self.observing(reasoning)
            
            if not papers:
                logger.info("今日未发现相关论文")
                return
            
            # Acting: 增强执行阶段
            analysis_results = self.acting(papers)
            
            logger.info("增强版arXiv论文监控Agent运行完成！")
            
            # 返回分析结果供进一步处理
            return analysis_results
            
        except Exception as e:
            logger.error(f"增强版Agent运行失败: {e}")
            raise

if __name__ == "__main__":
    agent = EnhancedArxivAgent()
    agent.run()

