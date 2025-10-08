#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署和配置工具
用于设置和测试arXiv监控Agent
"""

import os
import sys
import yaml
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List

class DeploymentHelper:
    """部署助手类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "config.yaml"
        
    def check_dependencies(self) -> bool:
        """检查依赖是否安装"""
        print("🔍 检查依赖...")
        
        required_packages = [
            'requests', 'feedparser', 'openai', 'python-dotenv',
            'schedule', 'PyYAML', 'markdown', 'beautifulsoup4', 'lxml'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package}")
        
        if missing_packages:
            print(f"\n缺少依赖包: {', '.join(missing_packages)}")
            print("请运行: pip install -r requirements.txt")
            return False
        
        print("✅ 所有依赖已安装")
        return True
    
    def setup_environment(self) -> bool:
        """设置环境变量"""
        print("🔧 设置环境变量...")
        
        env_example = self.project_root / "env_example.txt"
        env_file = self.project_root / ".env"
        
        if not env_file.exists():
            if env_example.exists():
                shutil.copy(env_example, env_file)
                print("✅ 已创建 .env 文件")
                print("⚠️  请编辑 .env 文件，填入您的API密钥")
            else:
                print("❌ 找不到 env_example.txt 文件")
                return False
        else:
            print("✅ .env 文件已存在")
        
        return True
    
    def validate_config(self) -> bool:
        """验证配置文件"""
        print("📋 验证配置文件...")
        
        if not self.config_file.exists():
            print("❌ 配置文件不存在")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            required_sections = ['arxiv', 'ai_model', 'output']
            for section in required_sections:
                if section not in config:
                    print(f"❌ 配置文件缺少 {section} 部分")
                    return False
            
            print("✅ 配置文件验证通过")
            return True
            
        except Exception as e:
            print(f"❌ 配置文件验证失败: {e}")
            return False
    
    def test_arxiv_connection(self) -> bool:
        """测试arXiv连接"""
        print("🌐 测试arXiv连接...")
        
        try:
            import feedparser
            import requests
            
            # 测试RSS feed
            test_url = "http://arxiv.org/rss/cs.AI"
            feed = feedparser.parse(test_url)
            
            if feed.entries:
                print(f"✅ arXiv连接正常，获取到 {len(feed.entries)} 篇论文")
                return True
            else:
                print("❌ arXiv连接失败，无法获取论文")
                return False
                
        except Exception as e:
            print(f"❌ arXiv连接测试失败: {e}")
            return False
    
    def test_ai_api(self) -> bool:
        """测试AI API连接"""
        print("🤖 测试AI API连接...")
        
        try:
            from dotenv import load_dotenv
            import openai
            
            load_dotenv()
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("❌ 未找到OPENAI_API_KEY环境变量")
                return False
            
            client = openai.OpenAI(api_key=api_key)
            
            # 发送测试请求
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10
            )
            
            if response.choices:
                print("✅ AI API连接正常")
                return True
            else:
                print("❌ AI API响应异常")
                return False
                
        except Exception as e:
            print(f"❌ AI API测试失败: {e}")
            return False
    
    def create_output_directory(self) -> bool:
        """创建输出目录"""
        print("📁 创建输出目录...")
        
        try:
            output_dir = self.project_root / "papers"
            output_dir.mkdir(exist_ok=True)
            
            # 创建.gitkeep文件
            gitkeep_file = output_dir / ".gitkeep"
            gitkeep_file.touch()
            
            print("✅ 输出目录创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 输出目录创建失败: {e}")
            return False
    
    def run_test(self) -> bool:
        """运行测试"""
        print("🧪 运行测试...")
        
        try:
            # 运行基础Agent测试
            from arxiv_agent import ArxivAgent
            
            # 创建临时配置文件用于测试
            test_config = {
                'arxiv': {
                    'categories': ['cs.AI'],
                    'keywords': ['machine learning'],
                    'max_papers_per_day': 2
                },
                'ai_model': {
                    'provider': 'deepseek',
                    'deepseek': {
                        'model': 'deepseek-chat',
                        'api_key_env': 'DEEPSEEK_API_KEY',
                        'base_url': 'https://api.deepseek.com'
                    },
                    'analysis_prompt': '请简要分析这篇论文的核心内容。'
                },
                'output': {
                    'output_dir': 'papers',
                    'filename_format': '{date}_test_papers.md',
                    'date_format': '%Y-%m-%d'
                }
            }
            
            with open('test_config.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(test_config, f, default_flow_style=False, allow_unicode=True)
            
            # 运行测试
            agent = ArxivAgent('test_config.yaml')
            agent.run()
            
            # 清理测试文件
            os.remove('test_config.yaml')
            
            print("✅ 测试运行成功")
            return True
            
        except Exception as e:
            print(f"❌ 测试运行失败: {e}")
            return False
    
    def setup_git_hooks(self) -> bool:
        """设置Git钩子"""
        print("🔗 设置Git钩子...")
        
        try:
            git_dir = self.project_root / ".git"
            if not git_dir.exists():
                print("❌ 这不是一个Git仓库")
                return False
            
            hooks_dir = git_dir / "hooks"
            hooks_dir.mkdir(exist_ok=True)
            
            # 创建pre-commit钩子
            pre_commit_hook = hooks_dir / "pre-commit"
            with open(pre_commit_hook, 'w') as f:
                f.write("""#!/bin/sh
# 运行代码检查
python -m py_compile arxiv_agent.py
python -m py_compile enhanced_agent.py
""")
            
            pre_commit_hook.chmod(0o755)
            
            print("✅ Git钩子设置成功")
            return True
            
        except Exception as e:
            print(f"❌ Git钩子设置失败: {e}")
            return False
    
    def generate_readme(self) -> bool:
        """生成README文件"""
        print("📖 生成README文件...")
        
        readme_content = """# arXiv论文监控Agent

基于React思考流程的智能arXiv论文监控系统，能够自动抓取、分析和报告最新研究论文。

## 功能特性

- 🔍 **智能监控**: 基于关键词和分类的智能论文筛选
- 🤖 **AI分析**: 集成多种AI模型进行深度论文分析
- 📊 **相关性评分**: 自动计算论文相关性评分
- 💻 **源码检测**: 自动识别论文中的源码链接
- 📝 **Markdown报告**: 生成结构化的Markdown格式报告
- ⚡ **自动部署**: 支持GitHub Actions自动部署
- 🔄 **定时运行**: 每日自动运行并更新报告

## 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone <your-repo-url>
cd arxiv_agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env_example.txt .env
# 编辑 .env 文件，填入您的API密钥
```

### 2. 配置设置

编辑 `config.yaml` 文件，设置：
- 监控的arXiv分类
- 关键词过滤
- AI模型配置
- 输出设置

### 3. 运行测试

```bash
python deploy.py --test
```

### 4. 手动运行

```bash
python arxiv_agent.py
```

### 5. GitHub Actions部署

1. 在GitHub仓库中设置Secrets：
   - `OPENAI_API_KEY`: OpenAI API密钥
   - `GITHUB_TOKEN`: GitHub访问令牌

2. 推送代码到GitHub，Actions将自动运行

## 配置说明

### arXiv配置

```yaml
arxiv:
  categories:
    - "cs.AI"      # 人工智能
    - "cs.LG"      # 机器学习
    - "cs.CV"      # 计算机视觉
  
  keywords:
    - "large language model"
    - "transformer"
    - "neural network"
  
  max_papers_per_day: 10
```

### AI模型配置

```yaml
ai_model:
  provider: "openai"
  openai:
    model: "gpt-3.5-turbo"
    api_key_env: "OPENAI_API_KEY"
    base_url: "https://api.openai.com/v1"
```

## 输出格式

生成的Markdown报告包含：
- 论文基本信息（标题、作者、链接）
- 相关性评分
- 源码链接（如果存在）
- AI深度分析
- 关键洞察提取

## 故障排除

### 常见问题

1. **API密钥错误**: 检查.env文件中的API密钥配置
2. **网络连接问题**: 确保能够访问arXiv和AI API
3. **依赖包缺失**: 运行 `pip install -r requirements.txt`
4. **配置文件错误**: 检查config.yaml格式是否正确

### 日志查看

```bash
tail -f arxiv_agent.log
```

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License
"""
        
        readme_file = self.project_root / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ README文件生成成功")
        return True
    
    def run_full_setup(self) -> bool:
        """运行完整设置"""
        print("🚀 开始完整设置...")
        
        steps = [
            ("检查依赖", self.check_dependencies),
            ("设置环境变量", self.setup_environment),
            ("验证配置文件", self.validate_config),
            ("创建输出目录", self.create_output_directory),
            ("测试arXiv连接", self.test_arxiv_connection),
            ("测试AI API", self.test_ai_api),
            ("设置Git钩子", self.setup_git_hooks),
            ("生成README", self.generate_readme)
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*50}")
            print(f"步骤: {step_name}")
            print('='*50)
            
            if not step_func():
                print(f"❌ 步骤 '{step_name}' 失败")
                return False
        
        print("\n🎉 完整设置成功！")
        print("\n下一步：")
        print("1. 编辑 .env 文件，填入您的API密钥")
        print("2. 根据需要修改 config.yaml 配置")
        print("3. 运行测试: python deploy.py --test")
        print("4. 手动运行: python arxiv_agent.py")
        
        return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="arXiv监控Agent部署工具")
    parser.add_argument('--setup', action='store_true', help='运行完整设置')
    parser.add_argument('--test', action='store_true', help='运行测试')
    parser.add_argument('--check', action='store_true', help='检查环境')
    
    args = parser.parse_args()
    
    helper = DeploymentHelper()
    
    if args.setup:
        success = helper.run_full_setup()
    elif args.test:
        success = helper.run_test()
    elif args.check:
        success = (
            helper.check_dependencies() and
            helper.validate_config() and
            helper.test_arxiv_connection()
        )
    else:
        parser.print_help()
        return
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

