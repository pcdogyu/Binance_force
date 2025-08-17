#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全市场强平订单流测试脚本
"""

import sys
import os
import asyncio
import json
import websockets
from datetime import datetime

# 币安全市场强平订单WebSocket URL
BINANCE_WS_URL = "wss://fstream.binance.com/ws/!forceOrder@arr"

async def test_all_market_force_orders():
    """测试全市场强平订单流"""
    print("=" * 60)
    print("🌍 币安全市场强平订单流测试")
    print("=" * 60)
    print(f"📡 连接地址: {BINANCE_WS_URL}")
    print("💡 将接收所有币对的强平订单数据")
    print("⏰ 开始时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    try:
        # 连接到币安WebSocket
        print("🔌 正在连接到币安WebSocket...")
        async with websockets.connect(BINANCE_WS_URL) as websocket:
            print("✅ 连接成功！")
            print("🔄 等待强平订单数据...")
            print("💡 按 Ctrl+C 停止测试")
            print("-" * 60)
            
            # 接收消息
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # 检查是否为强平订单消息
                    if data.get("e") == "forceOrder":
                        order = data.get("o", {})
                        
                        # 在控制台打印详细信息
                        print("\n" + "🚨" * 20)
                        print("🚨 收到强平订单!")
                        print("🚨" * 20)
                        print(f"🏷️  交易对: {order.get('s', 'N/A')}")
                        print(f"📈 方向: {order.get('S', 'N/A')}")
                        print(f"📊 数量: {order.get('q', 'N/A')}")
                        print(f"💰 价格: {order.get('p', 'N/A')}")
                        print(f"📝 订单类型: {order.get('o', 'N/A')}")
                        print(f"⏰ 时间: {datetime.fromtimestamp(data.get('E', 0)/1000).strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"📊 平均价格: {order.get('ap', 'N/A')}")
                        print(f"✅ 状态: {order.get('X', 'N/A')}")
                        print(f"📊 最近成交量: {order.get('l', 'N/A')}")
                        print(f"📊 累计成交量: {order.get('z', 'N/A')}")
                        print("🚨" * 20)
                        
                        # 同时保存到文件
                        save_to_file(data)
                        
                    else:
                        print(f"📡 收到其他消息: {data.get('e', 'unknown')}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                except Exception as e:
                    print(f"❌ 处理消息失败: {e}")
                    
    except websockets.exceptions.ConnectionClosed:
        print("⚠️ WebSocket连接已关闭")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

def save_to_file(data):
    """保存数据到文件"""
    try:
        filename = "all_market_force_orders.json"
        
        # 读取现有数据
        existing_data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        
        # 添加新数据
        order_info = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        existing_data.append(order_info)
        
        # 限制文件大小，保留最近1000条记录
        if len(existing_data) > 1000:
            existing_data = existing_data[-1000:]
        
        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据已保存到 {filename}")
        
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")

async def main():
    """主函数"""
    try:
        await test_all_market_force_orders()
    except KeyboardInterrupt:
        print("\n👋 测试已停止")
    except Exception as e:
        print(f"💥 测试异常: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 