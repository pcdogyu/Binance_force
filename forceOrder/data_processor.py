import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from config import SYMBOLS

logger = logging.getLogger(__name__)

class OfflineDataProcessor:
    """离线数据处理器，用于在没有InfluxDB的情况下处理数据"""
    
    def __init__(self):
        self.force_orders = []
        self.symbol_stats = {symbol: [] for symbol in SYMBOLS}
        self.data_file = "force_orders_data.json"
        self._load_data()
    
    def _load_data(self):
        """从文件加载数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.force_orders = data.get('force_orders', [])
                self.symbol_stats = data.get('symbol_stats', {symbol: [] for symbol in SYMBOLS})
            logger.info(f"从文件加载了 {len(self.force_orders)} 条强平订单数据")
        except FileNotFoundError:
            logger.info("数据文件不存在，将创建新的数据文件")
        except Exception as e:
            logger.error(f"加载数据文件失败: {e}")
    
    def _save_data(self):
        """保存数据到文件"""
        try:
            data = {
                'force_orders': self.force_orders,
                'symbol_stats': self.symbol_stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("数据已保存到文件")
        except Exception as e:
            logger.error(f"保存数据文件失败: {e}")
    
    def save_force_order(self, force_order_data: Dict[str, Any]):
        """保存强平订单数据"""
        try:
            # 添加时间戳
            order_info = {
                'timestamp': datetime.now().isoformat(),
                'data': force_order_data
            }
            
            # 保存到内存
            self.force_orders.append(order_info)
            
            # 按币对分类
            symbol = force_order_data['o']['s']
            if symbol in self.symbol_stats:
                self.symbol_stats[symbol].append(order_info)
            
            # 限制内存中的数据量（保留最近1000条）
            if len(self.force_orders) > 1000:
                self.force_orders = self.force_orders[-1000:]
                for sym in self.symbol_stats:
                    if len(self.symbol_stats[sym]) > 100:
                        self.symbol_stats[sym] = self.symbol_stats[sym][-100:]
            
            # 保存到文件
            self._save_data()
            
            logger.info(f"成功保存强平订单数据: {symbol}")
            
        except Exception as e:
            logger.error(f"保存强平订单数据失败: {e}")
    
    def query_force_orders_by_symbol(self, symbol: str, hours: int = 24, limit: int = 100):
        """查询指定币对的强平订单"""
        try:
            if symbol not in self.symbol_stats:
                logger.warning(f"未找到币对 {symbol} 的数据")
                return []
            
            # 过滤最近N小时的数据
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            recent_orders = []
            
            for order in self.symbol_stats[symbol]:
                try:
                    order_time = datetime.fromisoformat(order['timestamp']).timestamp()
                    if order_time >= cutoff_time:
                        recent_orders.append(order)
                except:
                    continue
            
            # 限制返回数量
            recent_orders = recent_orders[-limit:]
            
            logger.info(f"找到 {symbol} 最近 {hours} 小时的 {len(recent_orders)} 条强平订单")
            return recent_orders
            
        except Exception as e:
            logger.error(f"查询失败: {e}")
            return []
    
    def query_all_force_orders(self, hours: int = 24):
        """查询所有币对的强平订单统计"""
        try:
            logger.info(f"查询最近 {hours} 小时所有币对的强平订单统计...")
            
            for symbol in SYMBOLS:
                print(f"\n=== {symbol} 强平订单统计 ===")
                orders = self.query_force_orders_by_symbol(symbol, hours, 10)
                
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
                    print("无强平订单数据")
                    
        except Exception as e:
            logger.error(f"查询失败: {e}")
    
    def query_force_orders_summary(self, hours: int = 24):
        """查询强平订单汇总信息"""
        try:
            logger.info(f"查询最近 {hours} 小时强平订单汇总...")
            
            total_count = 0
            symbol_counts = {}
            
            for symbol in SYMBOLS:
                orders = self.query_force_orders_by_symbol(symbol, hours)
                count = len(orders)
                symbol_counts[symbol] = count
                total_count += count
            
            print(f"总强平订单数: {total_count}")
            
            for symbol, count in symbol_counts.items():
                print(f"{symbol}: {count} 条")
                
        except Exception as e:
            logger.error(f"查询汇总失败: {e}")
    
    def get_data_summary(self):
        """获取数据摘要"""
        return {
            'total_orders': len(self.force_orders),
            'symbol_counts': {symbol: len(orders) for symbol, orders in self.symbol_stats.items()},
            'last_updated': datetime.now().isoformat()
        } 