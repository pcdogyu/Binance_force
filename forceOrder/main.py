import asyncio
import logging
import signal
import sys
from typing import Dict, Any
from config import LOG_LEVEL, LOG_FORMAT, MONITOR_MODE
from websocket_client import BinanceWebSocketClient
from influxdb_handler import InfluxDBHandler
from data_processor import OfflineDataProcessor

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('force_order_monitor.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class ForceOrderMonitor:
    """强平订单监控器"""
    
    def __init__(self):
        self.influxdb_handler = None
        self.offline_processor = None
        self.websocket_client = None
        self.running = False
        self.use_offline_mode = False
        
    async def start(self):
        """启动监控器"""
        try:
            logger.info("=" * 60)
            logger.info("🚀 正在启动币安强平订单监控系统...")
            logger.info("=" * 60)
            
            # 显示监控模式
            if MONITOR_MODE == "all_market":
                logger.info("🌍 监控模式: 全市场强平订单")
                logger.info("💡 将接收所有币对的强平订单数据")
                logger.info("📊 使用流: !forceOrder@arr")
            else:
                logger.info("🎯 监控模式: 特定币对强平订单")
                logger.info("📋 监控币对: SOL, ADA, DOGE, XRP, XLM")
            
            # 尝试初始化InfluxDB处理器
            try:
                logger.info("📊 正在初始化InfluxDB处理器...")
                self.influxdb_handler = InfluxDBHandler()
                self.use_offline_mode = False
                logger.info("✅ InfluxDB处理器初始化完成")
                
                # 显示数据库信息
                logger.info("📋 获取数据库信息...")
                db_info = self.influxdb_handler.get_database_info()
                if db_info:
                    logger.info("📊 数据库信息:")
                    logger.info(f"  组织: {db_info.get('organizations', [])}")
                    logger.info(f"  存储桶: {db_info.get('buckets', [])}")
                    logger.info(f"  测量: {db_info.get('measurements', [])}")
                
            except Exception as e:
                logger.warning(f"⚠️ InfluxDB连接失败，切换到离线模式: {e}")
                logger.info("📁 正在初始化离线数据处理器...")
                self.offline_processor = OfflineDataProcessor()
                self.use_offline_mode = True
                logger.info("✅ 离线数据处理器初始化完成")
            
            # 初始化WebSocket客户端
            logger.info("🌐 正在初始化WebSocket客户端...")
            self.websocket_client = BinanceWebSocketClient(self.handle_force_order)
            logger.info("✅ WebSocket客户端初始化完成")
            
            # 设置信号处理
            self.setup_signal_handlers()
            
            # 启动监控
            self.running = True
            logger.info("🔄 正在启动监控...")
            await self.websocket_client.connect()
            
        except Exception as e:
            logger.error(f"❌ 启动监控器失败: {e}")
            await self.cleanup()
            sys.exit(1)
    
    async def handle_force_order(self, data: Dict[str, Any]):
        """处理强平订单数据"""
        try:
            logger.info("🎯 收到新的强平订单数据")
            
            # 根据模式保存数据
            if self.use_offline_mode and self.offline_processor:
                logger.info("💾 使用离线模式保存数据...")
                self.offline_processor.save_force_order(data)
            elif self.influxdb_handler:
                logger.info("💾 使用InfluxDB模式保存数据...")
                self.influxdb_handler.save_force_order(data)
            
            # 打印详细信息
            order = data.get("o", {})
            logger.info(f"""
📋 强平订单详情:
  🏷️  交易对: {order.get('s', 'N/A')}
  📈 方向: {order.get('S', 'N/A')}
  📝 订单类型: {order.get('o', 'N/A')}
  📊 数量: {order.get('q', 'N/A')}
  💰 价格: {order.get('p', 'N/A')}
  📊 平均价格: {order.get('ap', 'N/A')}
  ✅ 状态: {order.get('X', 'N/A')}
  🕐 时间: {data.get('E', 'N/A')}
  💾 存储模式: {'离线模式' if self.use_offline_mode else 'InfluxDB模式'}
            """)
            
        except Exception as e:
            logger.error(f"❌ 处理强平订单失败: {e}")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误详情: {str(e)}")
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"📡 收到信号 {signum}，正在关闭...")
            self.running = False
            asyncio.create_task(self.cleanup())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 正在清理资源...")
        
        if self.websocket_client:
            logger.info("🔌 正在断开WebSocket连接...")
            await self.websocket_client.disconnect()
        
        if self.influxdb_handler:
            logger.info("🗄️ 正在关闭InfluxDB连接...")
            self.influxdb_handler.close()
        
        if self.offline_processor:
            logger.info("💾 正在保存离线数据...")
            self.offline_processor._save_data()
        
        logger.info("✅ 资源清理完成")
    
    async def run(self):
        """运行监控器"""
        try:
            await self.start()
            
            # 保持运行状态
            logger.info("🔄 监控系统正在运行中...")
            if MONITOR_MODE == "all_market":
                logger.info("🌍 监控全市场强平订单，等待数据...")
            else:
                logger.info("🎯 监控指定币对强平订单，等待数据...")
            logger.info("💡 按 Ctrl+C 停止监控")
            
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("⌨️ 收到中断信号，正在关闭...")
        except Exception as e:
            logger.error(f"❌ 运行时发生错误: {e}")
        finally:
            await self.cleanup()

async def main():
    """主函数"""
    monitor = ForceOrderMonitor()
    await monitor.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 程序已退出")
    except Exception as e:
        logger.error(f"💥 程序异常退出: {e}")
        sys.exit(1) 