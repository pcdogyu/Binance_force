#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安强平订单监控系统测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'forceOrder'))

def test_imports():
    """测试模块导入"""
    try:
        print("测试模块导入...")
        
        # 测试配置导入
        from config import SYMBOLS, INFLUXDB_CONFIG, LOG_LEVEL
        print(f"✅ 配置导入成功: {len(SYMBOLS)} 个币对")
        
        # 测试WebSocket客户端导入
        from websocket_client import BinanceWebSocketClient
        print("✅ WebSocket客户端导入成功")
        
        # 测试InfluxDB处理器导入
        from influxdb_handler import InfluxDBHandler
        print("✅ InfluxDB处理器导入成功")
        
        print("\n🎉 所有模块导入成功！")
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config():
    """测试配置"""
    try:
        print("\n测试配置...")
        
        from config import SYMBOLS, INFLUXDB_CONFIG, LOG_LEVEL
        
        print(f"监控币对: {', '.join(SYMBOLS)}")
        print(f"InfluxDB URL: {INFLUXDB_CONFIG['url']}")
        print(f"存储桶: {INFLUXDB_CONFIG['bucket']}")
        print(f"日志级别: {LOG_LEVEL}")
        
        print("✅ 配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_websocket_url():
    """测试WebSocket URL构建"""
    try:
        print("\n测试WebSocket URL构建...")
        
        from config import BINANCE_WS_BASE_URL, SYMBOLS
        
        streams = [f"{symbol.lower()}@forceorder" for symbol in SYMBOLS]
        ws_url = f"{BINANCE_WS_BASE_URL}/{'/'.join(streams)}"
        
        print(f"WebSocket URL: {ws_url}")
        print("✅ WebSocket URL构建成功")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket URL构建失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("币安强平订单监控系统测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_websocket_url
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统准备就绪。")
        print("\n下一步:")
        print("1. 配置InfluxDB连接信息")
        print("2. 运行: python forceOrder/main.py")
        print("3. 或使用: start_monitor.bat")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 