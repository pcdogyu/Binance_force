import asyncio
import logging
from datetime import datetime, timedelta
from influxdb_handler import InfluxDBHandler
from data_processor import OfflineDataProcessor
from config import SYMBOLS, INFLUXDB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForceOrderQueryTool:
    """强平订单查询工具"""
    
    def __init__(self):
        self.influxdb_handler = None
        self.offline_processor = None
        self.use_offline_mode = False
        self._initialize_handlers()
    
    def _initialize_handlers(self):
        """初始化数据处理器"""
        try:
            # 尝试连接InfluxDB
            self.influxdb_handler = InfluxDBHandler()
            self.use_offline_mode = False
            logger.info("使用InfluxDB模式")
        except Exception as e:
            logger.warning(f"InfluxDB连接失败，切换到离线模式: {e}")
            self.offline_processor = OfflineDataProcessor()
            self.use_offline_mode = True
            logger.info("使用离线模式")
    
    def query_force_orders_by_symbol(self, symbol: str, hours: int = 24, limit: int = 100):
        """查询指定币对的强平订单"""
        try:
            logger.info(f"查询 {symbol} 最近 {hours} 小时的强平订单...")
            
            if self.use_offline_mode:
                # 离线模式查询
                orders = self.offline_processor.query_force_orders_by_symbol(symbol, hours, limit)
                if orders:
                    for order in orders:
                        data = order['data']['o']
                        print(f"""
时间: {order['timestamp']}
交易对: {data.get('s', 'N/A')}
方向: {data.get('S', 'N/A')}
数量: {data.get('q', 'N/A')}
价格: {data.get('p', 'N/A')}
状态: {data.get('X', 'N/A')}
                        """)
                else:
                    print(f"未找到 {symbol} 的强平订单记录")
            else:
                # InfluxDB模式查询
                query = f'''
                from(bucket: "{INFLUXDB_CONFIG["bucket"]}")
                    |> range(start: -{hours}h)
                    |> filter(fn: (r) => r["_measurement"] == "{INFLUXDB_CONFIG["measurement"]}")
                    |> filter(fn: (r) => r["symbol"] == "{symbol}")
                    |> sort(columns: ["_time"], desc: true)
                    |> limit(n: {limit})
                '''
                
                result = self.influxdb_handler.query_api.query(query)
                
                if result:
                    logger.info(f"找到 {len(result)} 条记录")
                    for record in result:
                        print(f"""
时间: {record.get_time()}
交易对: {record.values.get('symbol', 'N/A')}
方向: {record.values.get('side', 'N/A')}
数量: {record.values.get('_value', 'N/A')}
价格: {record.values.get('price', 'N/A')}
                        """)
                else:
                    logger.info(f"未找到 {symbol} 的强平订单记录")
                
        except Exception as e:
            logger.error(f"查询失败: {e}")
    
    def query_all_force_orders(self, hours: int = 24):
        """查询所有币对的强平订单统计"""
        try:
            logger.info(f"查询最近 {hours} 小时所有币对的强平订单统计...")
            
            if self.use_offline_mode:
                self.offline_processor.query_all_force_orders(hours)
            else:
                for symbol in SYMBOLS:
                    print(f"\n=== {symbol} 强平订单统计 ===")
                    self.query_force_orders_by_symbol(symbol, hours, 10)
                
        except Exception as e:
            logger.error(f"查询失败: {e}")
    
    def query_force_orders_summary(self, hours: int = 24):
        """查询强平订单汇总信息"""
        try:
            logger.info(f"查询最近 {hours} 小时强平订单汇总...")
            
            if self.use_offline_mode:
                self.offline_processor.query_force_orders_summary(hours)
            else:
                # InfluxDB模式查询
                total_query = f'''
                from(bucket: "{INFLUXDB_CONFIG["bucket"]}")
                    |> range(start: -{hours}h)
                    |> filter(fn: (r) => r["_measurement"] == "{INFLUXDB_CONFIG["measurement"]}")
                    |> count()
                '''
                
                total_result = self.influxdb_handler.query_api.query(total_query)
                total_count = len(list(total_result)) if total_result else 0
                
                print(f"总强平订单数: {total_count}")
                
                # 按币对统计
                for symbol in SYMBOLS:
                    symbol_query = f'''
                    from(bucket: "{INFLUXDB_CONFIG["bucket"]}")
                        |> range(start: -{hours}h)
                        |> filter(fn: (r) => r["_measurement"] == "{INFLUXDB_CONFIG["measurement"]}")
                        |> filter(fn: (r) => r["symbol"] == "{symbol}")
                        |> count()
                    '''
                    
                    symbol_result = self.influxdb_handler.query_api.query(symbol_query)
                    symbol_count = len(list(symbol_result)) if symbol_result else 0
                    
                    print(f"{symbol}: {symbol_count} 条")
                
        except Exception as e:
            logger.error(f"查询汇总失败: {e}")
    
    def get_data_summary(self):
        """获取数据摘要"""
        if self.use_offline_mode:
            return self.offline_processor.get_data_summary()
        else:
            return {"mode": "InfluxDB", "status": "connected"}
    
    def close(self):
        """关闭连接"""
        if self.influxdb_handler:
            self.influxdb_handler.close()
        if self.offline_processor:
            self.offline_processor._save_data()

def main():
    """主函数"""
    tool = ForceOrderQueryTool()
    
    try:
        while True:
            print("\n=== 强平订单查询工具 ===")
            print(f"当前模式: {'离线模式' if tool.use_offline_mode else 'InfluxDB模式'}")
            print("1. 查询指定币对强平订单")
            print("2. 查询所有币对强平订单")
            print("3. 查询强平订单汇总")
            print("4. 查看数据摘要")
            print("5. 退出")
            
            choice = input("请选择操作 (1-5): ").strip()
            
            if choice == "1":
                symbol = input("请输入币对 (如: SOLUSDT): ").strip().upper()
                if symbol in SYMBOLS:
                    hours = int(input("请输入查询小时数 (默认24): ") or "24")
                    tool.query_force_orders_by_symbol(symbol, hours)
                else:
                    print(f"不支持的币对: {symbol}")
                    print(f"支持的币对: {', '.join(SYMBOLS)}")
            
            elif choice == "2":
                hours = int(input("请输入查询小时数 (默认24): ") or "24")
                tool.query_all_force_orders(hours)
            
            elif choice == "3":
                hours = int(input("请输入查询小时数 (默认24): ") or "24")
                tool.query_force_orders_summary(hours)
            
            elif choice == "4":
                summary = tool.get_data_summary()
                print("\n=== 数据摘要 ===")
                for key, value in summary.items():
                    print(f"{key}: {value}")
            
            elif choice == "5":
                print("退出程序...")
                break
            
            else:
                print("无效选择，请重新输入")
                
    except KeyboardInterrupt:
        print("\n程序已退出")
    finally:
        tool.close()

if __name__ == "__main__":
    main() 