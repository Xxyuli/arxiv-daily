# arXiv论文监控Agent

基于React思考流程（Reasoning-Observing-Acting）的智能arXiv论文监控系统，能够自动抓取、分析和报告最新研究论文。

## 🚀 快速开始

### 一键式设置（推荐新手）

```bash
# 克隆或下载项目文件到本地
cd arxiv_agent

# 运行快速开始向导
python quick_start.py
```

### 手动设置

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp env_example.txt .env
# 编辑 .env 文件，填入您的API密钥

# 3. 运行设置检查
python deploy.py --setup

# 4. 运行Agent
python run.py --enhanced
```

## ✨ 主要功能

- 🔍 **智能监控**: 基于关键词和分类自动筛选相关论文
- 🤖 **AI深度分析**: 使用大语言模型进行论文内容分析
- 📊 **相关性评分**: 自动计算论文与关注领域的相关性
- 💻 **源码检测**: 自动识别论文中的源码链接
- 📝 **结构化报告**: 生成Markdown格式的分析报告
- ⚡ **自动部署**: 支持GitHub Actions每日自动运行
- 🔄 **定时更新**: 根据arXiv更新时间自动获取最新论文

## 📁 项目结构

```
arxiv_agent/
├── arxiv_agent.py          # 基础版Agent（React流程）
├── enhanced_agent.py       # 增强版Agent（更多功能）
├── deploy.py               # 部署和配置工具
├── run.py                  # 运行脚本
├── quick_start.py          # 快速开始向导
├── config.yaml             # 配置文件
├── requirements.txt        # Python依赖
├── env_example.txt         # 环境变量模板
├── .github/
│   └── workflows/
│       └── arxiv_monitor.yml  # GitHub Actions配置
├── papers/                 # 生成的报告目录
├── DEPLOYMENT_GUIDE.md     # 详细部署指南
└── README.md              # 项目说明
```

## ⚙️ 配置说明

### 基本配置

编辑 `config.yaml` 文件：

```yaml
arxiv:
  categories:
    - "cs.AI"      # 监控的arXiv分类
    - "cs.LG"
    - "cs.CV"
  
  keywords:
    - "large language model"
    - "transformer"
    - "neural network"
  
  max_papers_per_day: 10

ai_model:
  provider: "openai"
  openai:
    model: "gpt-3.5-turbo"
    api_key_env: "OPENAI_API_KEY"

output:
  output_dir: "papers"
  filename_format: "{date}_papers.md"
```

### 环境变量

创建 `.env` 文件：

```bash
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_token_here
```

## 🎯 使用方法

### 本地运行

```bash
# 基础模式
python run.py

# 增强模式（推荐）
python run.py --enhanced

# 测试模式
python run.py --test

# 详细日志
python run.py --enhanced --verbose
```

### GitHub Actions部署

1. 将代码推送到GitHub仓库
2. 在仓库设置中添加Secrets：
   - `OPENAI_API_KEY`: OpenAI API密钥
   - `GITHUB_TOKEN`: GitHub访问令牌
3. GitHub Actions将每天自动运行

## 📊 输出示例

生成的Markdown报告包含：

- 论文基本信息（标题、作者、链接）
- 相关性评分
- 源码链接（如果存在）
- AI深度分析
- 关键洞察提取

## 🔧 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

2. **API密钥错误**
   - 检查 `.env` 文件中的API密钥配置
   - 确保API密钥有效且有足够配额

3. **网络连接问题**
   - 检查网络连接
   - 尝试使用VPN（如果在某些地区）

### 获取帮助

```bash
# 运行环境检查
python deploy.py --check

# 运行测试
python deploy.py --test

# 查看日志
tail -f arxiv_agent.log
```

## 📚 详细文档

- [完整部署指南](DEPLOYMENT_GUIDE.md) - 详细的部署和使用说明
- [配置文件说明](config.yaml) - 配置参数详细说明
- [GitHub Actions配置](.github/workflows/arxiv_monitor.yml) - 自动部署配置

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License

---

**开始使用**: 运行 `python quick_start.py` 开始您的arXiv论文监控之旅！

