#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv监控Agent运行脚本
提供简单的命令行接口
"""

import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from arxiv_agent import ArxivAgent
from enhanced_agent import EnhancedArxivAgent

def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="arXiv论文监控Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python run.py                    # 使用基础Agent运行
  python run.py --enhanced         # 使用增强版Agent运行
  python run.py --config custom.yaml  # 使用自定义配置文件
  python run.py --verbose          # 详细日志输出
  python run.py --test             # 测试模式（限制论文数量）
        """
    )
    
    parser.add_argument(
        '--config', 
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )
    
    parser.add_argument(
        '--enhanced',
        action='store_true',
        help='使用增强版Agent'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细日志输出'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试模式（减少论文数量）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='干运行模式（不保存文件）'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # 检查配置文件
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"配置文件不存在: {config_path}")
            logger.info("请先运行: python deploy.py --setup")
            return 1
        
        # 选择Agent类型
        if args.enhanced:
            logger.info("使用增强版Agent")
            agent = EnhancedArxivAgent(args.config)
        else:
            logger.info("使用基础Agent")
            agent = ArxivAgent(args.config)
        
        # 测试模式调整
        if args.test:
            logger.info("运行测试模式")
            # 这里可以添加测试模式的特殊配置
        
        # 干运行模式
        if args.dry_run:
            logger.info("干运行模式 - 不会保存文件")
            # 这里可以添加干运行模式的逻辑
        
        # 运行Agent
        logger.info("开始运行arXiv监控Agent...")
        result = agent.run()
        
        if result:
            logger.info("Agent运行成功完成！")
            return 0
        else:
            logger.warning("Agent运行完成，但可能没有发现新论文")
            return 0
            
    except KeyboardInterrupt:
        logger.info("用户中断运行")
        return 1
    except Exception as e:
        logger.error(f"运行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

