# arXiv论文监控Agent - 完整部署指南

本指南将帮助您从零开始部署arXiv论文监控Agent，即使您没有部署经验也能轻松上手。

## 📋 目录

1. [项目概述](#项目概述)
2. [环境准备](#环境准备)
3. [本地部署](#本地部署)
4. [GitHub Actions部署](#github-actions部署)
5. [配置说明](#配置说明)
6. [故障排除](#故障排除)
7. [高级功能](#高级功能)

## 🎯 项目概述

arXiv论文监控Agent是一个基于React思考流程（Reasoning-Observing-Acting）的智能论文监控系统，具有以下特性：

- 🔍 **智能监控**: 自动监控指定arXiv分类的最新论文
- 🤖 **AI分析**: 使用大语言模型深度分析论文内容
- 📊 **相关性评分**: 自动计算论文与您关注领域的相关性
- 💻 **源码检测**: 自动识别论文中的源码链接
- 📝 **Markdown报告**: 生成结构化的分析报告
- ⚡ **自动部署**: 支持GitHub Actions每日自动运行
- 🔄 **定时更新**: 根据arXiv更新时间自动获取最新论文

## 🛠 环境准备

### 系统要求

- **操作系统**: Windows 10+, macOS 10.14+, 或 Linux
- **Python版本**: 3.8 或更高版本
- **内存**: 至少 512MB 可用内存
- **网络**: 稳定的互联网连接

### 必需软件

1. **Python 3.8+**
   ```bash
   # 检查Python版本
   python --version
   
   # 如果没有Python，请访问 https://python.org 下载安装
   ```

2. **Git**（用于版本控制和GitHub Actions）
   ```bash
   # 检查Git是否安装
   git --version
   
   # 如果没有Git，请访问 https://git-scm.com 下载安装
   ```

3. **文本编辑器**（推荐VS Code或PyCharm）

## 🚀 本地部署

### 步骤1: 获取代码

```bash
# 方法1: 如果您有GitHub仓库
git clone https://github.com/your-username/arxiv-paper-monitor.git
cd arxiv-paper-monitor

# 方法2: 如果您只有源代码文件
# 将所有文件放在一个文件夹中，然后进入该文件夹
cd arxiv_agent
```

### 步骤2: 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

### 步骤3: 配置环境变量

```bash
# 复制环境变量模板
cp env_example.txt .env

# 编辑 .env 文件，填入您的API密钥
```

`.env` 文件内容示例：
```bash
# OpenAI API配置（必需）
OPENAI_API_KEY=sk-your-openai-api-key-here

# GitHub Token（用于GitHub Actions，可选）
GITHUB_TOKEN=ghp_your-github-token-here

# 其他可选配置
ANTHROPIC_API_KEY=your-anthropic-key-here
```

### 步骤4: 配置监控参数

编辑 `config.yaml` 文件：

```yaml
arxiv:
  # 监控的arXiv分类
  categories:
    - "cs.AI"      # 人工智能
    - "cs.LG"      # 机器学习
    - "cs.CV"      # 计算机视觉
    - "cs.CL"      # 计算语言学
  
  # 关键词过滤（论文标题或摘要包含这些关键词）
  keywords:
    - "large language model"
    - "transformer"
    - "neural network"
    - "deep learning"
    - "machine learning"
    - "artificial intelligence"
  
  # 每日最大论文数量
  max_papers_per_day: 10

ai_model:
  provider: "openai"
  openai:
    model: "gpt-3.5-turbo"
    api_key_env: "OPENAI_API_KEY"
    base_url: "https://api.openai.com/v1"

output:
  output_dir: "papers"
  filename_format: "{date}_papers.md"
  date_format: "%Y-%m-%d"
```

### 步骤5: 运行自动设置

```bash
# 运行完整设置（推荐新手使用）
python deploy.py --setup
```

这个命令会：
- ✅ 检查所有依赖是否正确安装
- ✅ 验证配置文件格式
- ✅ 测试arXiv连接
- ✅ 测试AI API连接
- ✅ 创建必要的目录
- ✅ 生成README文件

### 步骤6: 运行测试

```bash
# 运行测试模式（获取少量论文进行测试）
python deploy.py --test

# 或直接运行Agent
python run.py --test
```

### 步骤7: 手动运行

```bash
# 使用基础Agent
python run.py

# 使用增强版Agent（推荐）
python run.py --enhanced

# 详细日志输出
python run.py --enhanced --verbose
```

## ☁️ GitHub Actions部署

### 步骤1: 创建GitHub仓库

1. 访问 [GitHub](https://github.com)
2. 点击 "New repository"
3. 输入仓库名称（如：`arxiv-paper-monitor`）
4. 选择 "Public" 或 "Private"
5. 勾选 "Add a README file"
6. 点击 "Create repository"

### 步骤2: 推送代码到GitHub

```bash
# 初始化Git仓库（如果还没有）
git init

# 添加远程仓库
git remote add origin https://github.com/your-username/arxiv-paper-monitor.git

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: arXiv监控Agent"

# 推送到GitHub
git push -u origin main
```

### 步骤3: 配置GitHub Secrets

1. 在GitHub仓库页面，点击 "Settings" 标签
2. 在左侧菜单中找到 "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 添加以下Secrets：

| Secret名称 | 说明 | 示例值 |
|-----------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | `sk-...` |
| `GITHUB_TOKEN` | GitHub访问令牌 | `ghp_...` |

#### 如何获取GitHub Token：

1. 访问 [GitHub Settings](https://github.com/settings/tokens)
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 选择权限：
   - ✅ `repo` (完整仓库访问)
   - ✅ `workflow` (更新GitHub Actions工作流)
4. 点击 "Generate token"
5. 复制生成的token并保存到Secrets中

### 步骤4: 修改GitHub Actions配置

编辑 `.github/workflows/arxiv_monitor.yml` 文件中的仓库信息：

```yaml
# 在文件末尾找到这部分并修改
- name: 创建Issue（如果失败）
  uses: actions/github-script@v6
  with:
    script: |
      # 修改这里的仓库信息
      github.rest.issues.create({
        owner: "your-username",  # 改为您的用户名
        repo: "arxiv-paper-monitor",  # 改为您的仓库名
        title: title,
        body: body,
        labels: ['bug', 'arxiv-agent']
      });
```

### 步骤5: 启用GitHub Actions

1. 在GitHub仓库页面，点击 "Actions" 标签
2. 点击 "I understand my workflows, go ahead and enable them"
3. 您会看到 "arXiv论文监控Agent" 工作流
4. 点击该工作流，然后点击 "Run workflow" 进行测试

### 步骤6: 验证自动运行

GitHub Actions将在以下时间自动运行：
- **每天北京时间上午10点**（UTC时间凌晨2点）
- 您也可以手动触发运行

## ⚙️ 配置说明

### arXiv分类代码

常用分类代码：

| 分类代码 | 说明 |
|---------|------|
| `cs.AI` | 人工智能 |
| `cs.LG` | 机器学习 |
| `cs.CV` | 计算机视觉 |
| `cs.CL` | 计算语言学 |
| `cs.NE` | 神经网络与进化计算 |
| `cs.IR` | 信息检索 |
| `stat.ML` | 统计机器学习 |
| `math.ST` | 统计理论 |

### AI模型配置

#### OpenAI配置
```yaml
ai_model:
  provider: "openai"
  openai:
    model: "gpt-3.5-turbo"  # 或 "gpt-4"
    api_key_env: "OPENAI_API_KEY"
    base_url: "https://api.openai.com/v1"
```

#### Anthropic配置
```yaml
ai_model:
  provider: "anthropic"
  anthropic:
    model: "claude-3-sonnet-20240229"
    api_key_env: "ANTHROPIC_API_KEY"
```

### 自定义分析提示词

您可以自定义AI分析的内容：

```yaml
ai_model:
  analysis_prompt: |
    请对以下arXiv论文进行详细分析，包括：
    1. 论文的核心贡献和创新点
    2. 技术方法的优缺点
    3. 实验结果和性能分析
    4. 对领域发展的意义
    5. 潜在的应用场景
    6. 改进建议和未来研究方向
    
    请用中文回答，语言要专业但易懂。
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 依赖安装失败

**问题**: `pip install -r requirements.txt` 失败

**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或逐个安装
pip install requests feedparser openai python-dotenv
```

#### 2. OpenAI API连接失败

**问题**: `OpenAI API connection failed`

**解决方案**:
- ✅ 检查API密钥是否正确
- ✅ 检查网络连接
- ✅ 检查API配额是否充足
- ✅ 尝试使用VPN（如果在某些地区）

#### 3. arXiv连接超时

**问题**: `arXiv connection timeout`

**解决方案**:
```bash
# 检查网络连接
ping arxiv.org

# 使用代理（如果需要）
export https_proxy=http://your-proxy:port
export http_proxy=http://your-proxy:port
```

#### 4. GitHub Actions运行失败

**问题**: GitHub Actions工作流失败

**解决方案**:
1. 检查Secrets配置是否正确
2. 查看Actions运行日志
3. 确保仓库权限设置正确
4. 检查配置文件格式

#### 5. 没有发现相关论文

**问题**: Agent运行成功但没有生成报告

**解决方案**:
- ✅ 检查关键词设置是否过于严格
- ✅ 尝试扩大监控的arXiv分类
- ✅ 检查关键词拼写是否正确
- ✅ 降低相关性阈值

### 日志查看

```bash
# 查看Agent运行日志
tail -f arxiv_agent.log

# 查看详细日志
python run.py --enhanced --verbose

# 查看GitHub Actions日志
# 在GitHub仓库的Actions标签页中查看
```

## 🚀 高级功能

### 1. 使用增强版Agent

增强版Agent提供更多功能：

```bash
# 运行增强版Agent
python run.py --enhanced

# 增强版功能：
# - 相关性评分
# - 关键洞察提取
# - 多种AI提供商支持
# - 结构化数据输出
```

### 2. 自定义输出格式

修改 `config.yaml` 中的输出配置：

```yaml
output:
  output_dir: "papers"
  filename_format: "{date}_papers.md"
  date_format: "%Y-%m-%d"
```

### 3. 添加新的AI提供商

在 `enhanced_agent.py` 中添加新的AI提供商：

```python
def _setup_custom_provider(self):
    """设置自定义AI提供商"""
    # 实现您的自定义AI提供商逻辑
    pass
```

### 4. 自定义论文过滤逻辑

修改 `_enhanced_filter_papers` 方法：

```python
def _enhanced_filter_papers(self, papers, keywords):
    """自定义论文过滤逻辑"""
    # 实现您的过滤逻辑
    pass
```

### 5. 集成其他数据源

您可以扩展Agent来监控其他论文源：

```python
def _fetch_papers_from_other_sources(self):
    """从其他数据源获取论文"""
    # 实现其他数据源的集成
    pass
```

## 📞 获取帮助

如果您遇到问题，可以：

1. **查看日志文件**: `arxiv_agent.log`
2. **运行诊断**: `python deploy.py --check`
3. **查看GitHub Issues**: 在您的仓库中创建Issue
4. **检查配置**: 使用 `python deploy.py --test` 测试配置

## 🎉 完成！

恭喜！您已经成功部署了arXiv论文监控Agent。现在您可以：

- 📊 每天自动获取相关论文
- 🤖 使用AI进行深度分析
- 📝 生成结构化的Markdown报告
- 🔄 通过GitHub Actions自动更新

祝您使用愉快！如有问题，请随时查看日志文件或创建GitHub Issue。

