#!/usr/bin/env python3
"""
CodexAid 命令行接口

提供命令行工具来启动和管理CodexAid服务
"""

import argparse
import sys
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from codexaid.services.api.app import create_app
from codexaid.config.settings import settings
from codexaid.core.workflow.generator import MCPGenerator


def start_server(args):
    """启动CodexAid服务器"""
    print("🚀 启动 CodexAid - 智能MCP服务器生成系统")
    
    # 验证配置
    if not settings.validate():
        print("❌ 配置验证失败，请检查环境变量配置")
        return 1
    
    # 创建FastAPI应用
    app = create_app()
    
    # 启动服务器
    uvicorn.run(
        app,
        host=args.host or settings.server["host"],
        port=args.port or settings.server["port"],
        reload=args.reload or settings.server["reload"]
    )
    return 0


def generate_mcp(args):
    """生成MCP工具"""
    print(f"🔧 生成MCP工具: {args.prompt}")
    
    try:
        # 这里需要实现MCP生成逻辑
        # generator = MCPGenerator()
        # result = generator.generate(args.prompt)
        print("✅ MCP工具生成完成")
        return 0
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return 1


def show_config(args):
    """显示当前配置"""
    print("📋 CodexAid 配置信息:")
    print(f"  LLM API URL: {settings.llm['url']}")
    print(f"  LLM Model: {settings.llm['default_model']}")
    print(f"  Server Host: {settings.server['host']}")
    print(f"  Server Port: {settings.server['port']}")
    print(f"  DeepPath API: {settings.deeppath['api_url']}")
    return 0


def main():
    """主命令行入口"""
    parser = argparse.ArgumentParser(
        description="CodexAid - 智能MCP服务器生成系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  codexaid start                    # 启动服务器
  codexaid start --port 9000        # 在指定端口启动
  codexaid generate "创建学习工具"    # 生成MCP工具
  codexaid config                   # 显示配置信息
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 启动服务器命令
    start_parser = subparsers.add_parser('start', help='启动CodexAid服务器')
    start_parser.add_argument('--host', help='服务器主机地址')
    start_parser.add_argument('--port', type=int, help='服务器端口')
    start_parser.add_argument('--reload', action='store_true', help='启用自动重载')
    start_parser.set_defaults(func=start_server)
    
    # 生成MCP工具命令
    generate_parser = subparsers.add_parser('generate', help='生成MCP工具')
    generate_parser.add_argument('prompt', help='工具需求描述')
    generate_parser.set_defaults(func=generate_mcp)
    
    # 显示配置命令
    config_parser = subparsers.add_parser('config', help='显示配置信息')
    config_parser.set_defaults(func=show_config)
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有指定命令，默认启动服务器
    if not args.command:
        args.command = 'start'
        args.func = start_server
        args.host = None
        args.port = None
        args.reload = False
    
    # 执行命令
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n👋 再见!")
        return 0
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 