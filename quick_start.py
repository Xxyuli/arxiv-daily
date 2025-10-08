#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速开始脚本
为新手用户提供一键式设置和运行
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    arXiv论文监控Agent                        ║
    ║                  快速开始向导 v1.0                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("\n📦 安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def setup_environment():
    """设置环境变量"""
    print("\n🔧 设置环境变量...")
    
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if env_file.exists():
        print("✅ .env文件已存在")
        return True
    
    if not env_example.exists():
        print("❌ 找不到env_example.txt文件")
        return False
    
    # 复制模板文件
    with open(env_example, 'r', encoding='utf-8') as src:
        content = src.read()
    
    with open(env_file, 'w', encoding='utf-8') as dst:
        dst.write(content)
    
    print("✅ 已创建.env文件")
    print("⚠️  请编辑.env文件，填入您的API密钥")
    
    # 尝试打开文件进行编辑
    try:
        if sys.platform == "win32":
            os.startfile(str(env_file))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(env_file)])
        else:
            subprocess.run(["xdg-open", str(env_file)])
        print("📝 已尝试打开.env文件进行编辑")
    except:
        print("💡 请手动编辑.env文件")
    
    return True

def get_api_key():
    """获取API密钥"""
    print("\n🔑 配置API密钥...")
    
    api_key = input("请输入您的OpenAI API密钥 (或按Enter跳过): ").strip()
    
    if api_key:
        # 更新.env文件
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换API密钥
            content = content.replace("your_openai_api_key_here", api_key)
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ API密钥已保存")
            return True
    
    print("⚠️  请稍后手动编辑.env文件添加API密钥")
    return False

def run_test():
    """运行测试"""
    print("\n🧪 运行测试...")
    
    try:
        # 运行部署检查
        result = subprocess.run([sys.executable, "deploy.py", "--check"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 环境检查通过")
            return True
        else:
            print("❌ 环境检查失败")
            print("错误输出:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False

def run_agent():
    """运行Agent"""
    print("\n🚀 运行arXiv监控Agent...")
    
    try:
        # 询问用户选择
        print("\n请选择运行模式:")
        print("1. 基础模式 (推荐新手)")
        print("2. 增强模式 (更多功能)")
        print("3. 测试模式 (少量论文)")
        
        choice = input("请输入选择 (1-3, 默认1): ").strip() or "1"
        
        if choice == "1":
            cmd = [sys.executable, "run.py"]
        elif choice == "2":
            cmd = [sys.executable, "run.py", "--enhanced"]
        elif choice == "3":
            cmd = [sys.executable, "run.py", "--test"]
        else:
            cmd = [sys.executable, "run.py"]
        
        print(f"执行命令: {' '.join(cmd)}")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断运行")
    except Exception as e:
        print(f"❌ 运行失败: {e}")

def show_next_steps():
    """显示后续步骤"""
    print("\n" + "="*60)
    print("🎉 快速设置完成！")
    print("="*60)
    
    print("\n📋 后续步骤:")
    print("1. 确保.env文件中的API密钥配置正确")
    print("2. 根据需要修改config.yaml配置文件")
    print("3. 运行Agent: python run.py --enhanced")
    print("4. 查看生成的报告: papers/ 目录")
    
    print("\n📚 更多帮助:")
    print("- 详细部署指南: DEPLOYMENT_GUIDE.md")
    print("- 运行测试: python deploy.py --test")
    print("- 查看日志: tail -f arxiv_agent.log")
    
    print("\n🔧 常用命令:")
    print("- python run.py                    # 基础模式")
    print("- python run.py --enhanced         # 增强模式")
    print("- python run.py --test             # 测试模式")
    print("- python run.py --verbose          # 详细日志")
    print("- python deploy.py --setup         # 完整设置")

def main():
    """主函数"""
    print_banner()
    
    print("欢迎使用arXiv论文监控Agent快速开始向导！")
    print("这个向导将帮助您快速设置和运行Agent。")
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 安装依赖
    if not install_dependencies():
        print("\n❌ 依赖安装失败，请手动运行: pip install -r requirements.txt")
        return 1
    
    # 设置环境
    if not setup_environment():
        print("\n❌ 环境设置失败")
        return 1
    
    # 获取API密钥
    get_api_key()
    
    # 运行测试
    if not run_test():
        print("\n⚠️  测试失败，但您可以继续尝试运行Agent")
    
    # 询问是否立即运行
    run_now = input("\n是否立即运行Agent? (y/n, 默认n): ").strip().lower()
    if run_now in ['y', 'yes', '是']:
        run_agent()
    
    # 显示后续步骤
    show_next_steps()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)

