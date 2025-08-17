import json
import logging
import asyncio
import websockets
from typing import Dict, Any, Callable
from config import BINANCE_WS_BASE_URL, SYMBOLS, MONITOR_MODE, ALL_MARKET_STREAM

logger = logging.getLogger(__name__)

class BinanceWebSocketClient:
    """币安WebSocket客户端"""
    
    def __init__(self, message_handler: Callable[[Dict[str, Any]], None]):
        self.message_handler = message_handler
        self.websocket = None
        self.is_connected = False
        self.reconnect_delay = 5
        self.max_reconnect_delay = 300
        
    async def connect(self):
        """连接到币安WebSocket"""
        try:
            # 根据监控模式选择连接方式
            if MONITOR_MODE == "all_market":
                # 全市场强平订单流
                ws_url = f"{BINANCE_WS_BASE_URL}/{ALL_MARKET_STREAM}"
                logger.info(f"全市场模式: 正在连接到全市场强平订单流")
            else:
                # 特定币对强平订单流
                streams = [f"{symbol.lower()}@forceorder" for symbol in SYMBOLS]
                ws_url = f"{BINANCE_WS_BASE_URL}/{'/'.join(streams)}"
                logger.info(f"特定币对模式: 监控 {len(SYMBOLS)} 个币对")
            
            logger.info(f"正在连接到: {ws_url}")
            
            self.websocket = await websockets.connect(ws_url)
            self.is_connected = True
            logger.info("✅ 成功连接到币安WebSocket")
            
            if MONITOR_MODE == "all_market":
                logger.info("🌍 开始监控全市场强平订单...")
                logger.info("💡 将接收所有币对的强平订单数据")
            else:
                logger.info(f"🎯 开始监控指定币对: {', '.join(SYMBOLS)}")
            
            # 开始接收消息
            await self._receive_messages()
            
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            self.is_connected = False
            await self._handle_reconnect()
    
    async def _receive_messages(self):
        """接收WebSocket消息"""
        try:
            async for message in self.websocket:
                if message:
                    try:
                        data = json.loads(message)
                        await self._process_message(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ JSON解析失败: {e}")
                    except Exception as e:
                        logger.error(f"❌ 处理消息失败: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("⚠️ WebSocket连接已关闭")
            self.is_connected = False
            await self._handle_reconnect()
        except Exception as e:
            logger.error(f"❌ 接收消息时发生错误: {e}")
            self.is_connected = False
            await self._handle_reconnect()
    
    async def _process_message(self, data: Dict[str, Any]):
        """处理接收到的消息"""
        try:
            # 检查是否为强平订单消息
            if data.get("e") == "forceOrder":
                # 获取订单详情
                order = data.get("o", {})
                symbol = order.get("s", "UNKNOWN")
                side = order.get("S", "UNKNOWN")
                quantity = order.get("q", "0")
                price = order.get("p", "0")
                
                # 在控制台打印强平订单信息
                print("\n" + "="*60)
                print("🚨 收到强平订单!")
                print("="*60)
                print(f"🏷️  交易对: {symbol}")
                print(f"📈 方向: {side}")
                print(f"📊 数量: {quantity}")
                print(f"💰 价格: {price}")
                print(f"📝 订单类型: {order.get('o', 'N/A')}")
                print(f"⏰ 时间: {data.get('E', 'N/A')}")
                print(f"📊 平均价格: {order.get('ap', 'N/A')}")
                print(f"✅ 状态: {order.get('X', 'N/A')}")
                print("="*60)
                
                logger.info(f"🎯 收到强平订单: {symbol} - {side} - {quantity} @ {price}")
                
                # 调用消息处理器
                if self.message_handler:
                    await asyncio.create_task(self._handle_message_async(data))
                else:
                    self.message_handler(data)
            else:
                logger.debug(f"收到其他类型消息: {data.get('e', 'unknown')}")
                
        except Exception as e:
            logger.error(f"❌ 处理强平订单消息失败: {e}")
    
    async def _handle_message_async(self, data: Dict[str, Any]):
        """异步处理消息"""
        try:
            if asyncio.iscoroutinefunction(self.message_handler):
                await self.message_handler(data)
            else:
                self.message_handler(data)
        except Exception as e:
            logger.error(f"❌ 异步处理消息失败: {e}")
    
    async def _handle_reconnect(self):
        """处理重连"""
        if not self.is_connected:
            logger.info(f"⏳ 等待 {self.reconnect_delay} 秒后重连...")
            await asyncio.sleep(self.reconnect_delay)
            
            # 指数退避重连延迟
            self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
            
            await self.connect()
    
    async def disconnect(self):
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("🔌 WebSocket连接已断开")
    
    def get_connection_status(self) -> bool:
        """获取连接状态"""
        return self.is_connected
    
    def get_monitor_mode(self) -> str:
        """获取监控模式"""
        return MONITOR_MODE 