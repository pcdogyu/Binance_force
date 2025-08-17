import logging
from datetime import datetime
from typing import Dict, Any
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import INFLUXDB_CONFIG

logger = logging.getLogger(__name__)

class InfluxDBHandler:
    """InfluxDB数据处理器"""
    
    def __init__(self):
        self.client = None
        self.write_api = None
        self.query_api = None
        self.bucket = INFLUXDB_CONFIG["bucket"]
        self.measurement = INFLUXDB_CONFIG["measurement"]
        self.org = INFLUXDB_CONFIG["org"]
        self._connect()
    
    def _connect(self):
        """连接到InfluxDB"""
        try:
            logger.info(f"正在连接InfluxDB: {INFLUXDB_CONFIG['url']}")
            logger.info(f"组织: {self.org}, 存储桶: {self.bucket}, 测量: {self.measurement}")
            
            # 解析用户名和密码
            if ":" in INFLUXDB_CONFIG["token"]:
                username, password = INFLUXDB_CONFIG["token"].split(":", 1)
                logger.info(f"使用用户名密码认证: {username}")
            else:
                username = password = INFLUXDB_CONFIG["token"]
                logger.info("使用token认证")
            
            # 创建客户端连接
            if ":" in INFLUXDB_CONFIG["token"]:
                # 用户名密码认证
                self.client = InfluxDBClient(
                    url=INFLUXDB_CONFIG["url"],
                    username=username,
                    password=password,
                    org=self.org
                )
            else:
                # Token认证
                self.client = InfluxDBClient(
                    url=INFLUXDB_CONFIG["url"],
                    token=INFLUXDB_CONFIG["token"],
                    org=self.org
                )
            
            # 测试连接
            health = self.client.health()
            logger.info(f"InfluxDB健康状态: {health}")
            
            # 检查存储桶是否存在
            buckets_api = self.client.buckets_api()
            try:
                bucket_info = buckets_api.find_bucket_by_name(self.bucket)
                logger.info(f"存储桶 '{self.bucket}' 存在: {bucket_info}")
            except Exception as e:
                logger.warning(f"存储桶 '{self.bucket}' 不存在或无法访问: {e}")
                logger.info("请确保存储桶已创建且具有正确的权限")
                
                # 尝试创建存储桶
                try:
                    logger.info(f"尝试创建存储桶 '{self.bucket}'...")
                    bucket_info = buckets_api.create_bucket(
                        bucket_name=self.bucket,
                        org=self.org
                    )
                    logger.info(f"✅ 存储桶创建成功: {bucket_info}")
                except Exception as create_e:
                    logger.error(f"❌ 创建存储桶失败: {create_e}")
            
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            
            logger.info("✅ InfluxDB连接成功！")
            logger.info(f"写入API: {self.write_api}")
            logger.info(f"查询API: {self.query_api}")
            
        except Exception as e:
            logger.error(f"❌ 连接InfluxDB失败: {e}")
            logger.error(f"请检查以下配置:")
            logger.error(f"  - URL: {INFLUXDB_CONFIG['url']}")
            if ":" in INFLUXDB_CONFIG["token"]:
                username, password = INFLUXDB_CONFIG["token"].split(":", 1)
                logger.error(f"  - 用户名: {username}")
                logger.error(f"  - 密码: {password[:3]}...")
            else:
                logger.error(f"  - Token: {INFLUXDB_CONFIG['token'][:10]}...")
            logger.error(f"  - 组织: {self.org}")
            logger.error(f"  - 存储桶: {self.bucket}")
            raise
    
    def save_force_order(self, force_order_data: Dict[str, Any]):
        """保存强平订单数据到InfluxDB"""
        try:
            logger.info("=" * 50)
            logger.info("开始处理强平订单数据...")
            
            # 解析数据
            order = force_order_data.get("o", {})
            symbol = order.get("s", "UNKNOWN")
            side = order.get("S", "UNKNOWN")
            quantity = order.get("q", "0")
            price = order.get("p", "0")
            
            logger.info(f"订单详情:")
            logger.info(f"  交易对: {symbol}")
            logger.info(f"  方向: {side}")
            logger.info(f"  数量: {quantity}")
            logger.info(f"  价格: {price}")
            logger.info(f"  时间: {force_order_data.get('E', 'N/A')}")
            
            # 创建数据点
            logger.info("正在创建数据点...")
            point = Point(self.measurement) \
                .tag("symbol", symbol) \
                .tag("side", side) \
                .tag("order_type", order.get("o", "UNKNOWN")) \
                .tag("time_in_force", order.get("f", "UNKNOWN")) \
                .tag("status", order.get("X", "UNKNOWN")) \
                .field("quantity", float(quantity)) \
                .field("price", float(price)) \
                .field("avg_price", float(order.get("ap", "0"))) \
                .field("last_qty", float(order.get("l", "0"))) \
                .field("cum_qty", float(order.get("z", "0"))) \
                .time(datetime.fromtimestamp(force_order_data["E"] / 1000))
            
            logger.info(f"数据点创建完成: {point}")
            
            # 写入数据
            logger.info(f"正在写入数据到InfluxDB...")
            logger.info(f"  存储桶: {self.bucket}")
            logger.info(f"  组织: {self.org}")
            logger.info(f"  测量: {self.measurement}")
            
            self.write_api.write(
                bucket=self.bucket,
                org=self.org,
                record=point
            )
            
            logger.info("✅ 数据写入成功！")
            logger.info(f"已保存强平订单: {symbol} - {side} - {quantity} @ {price}")
            
            # 验证写入
            self._verify_write(symbol, side, quantity, price)
            
        except Exception as e:
            logger.error(f"❌ 保存强平订单数据失败: {e}")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误详情: {str(e)}")
            raise
    
    def _verify_write(self, symbol: str, side: str, quantity: str, price: str):
        """验证数据是否成功写入"""
        try:
            logger.info("正在验证数据写入...")
            
            # 查询最近写入的数据
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -1m)
                |> filter(fn: (r) => r["_measurement"] == "{self.measurement}")
                |> filter(fn: (r) => r["symbol"] == "{symbol}")
                |> filter(fn: (r) => r["side"] == "{side}")
                |> filter(fn: (r) => r["quantity"] == {quantity})
                |> filter(fn: (r) => r["price"] == {price})
                |> limit(n: 1)
            '''
            
            result = self.query_api.query(query)
            records = list(result)
            
            if records:
                logger.info(f"✅ 数据验证成功！找到 {len(records)} 条匹配记录")
                for record in records:
                    logger.info(f"  验证记录: {record}")
            else:
                logger.warning(f"⚠️ 数据验证: 未找到匹配的记录，可能需要等待数据同步")
                
        except Exception as e:
            logger.warning(f"数据验证失败: {e}")
    
    def query_recent_force_orders(self, symbol: str, limit: int = 100):
        """查询最近的强平订单"""
        try:
            logger.info(f"查询 {symbol} 最近 {limit} 条强平订单...")
            
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -24h)
                |> filter(fn: (r) => r["_measurement"] == "{self.measurement}")
                |> filter(fn: (r) => r["symbol"] == "{symbol}")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: {limit})
            '''
            
            logger.info(f"执行查询: {query}")
            result = self.query_api.query(query)
            records = list(result)
            
            logger.info(f"查询结果: 找到 {len(records)} 条记录")
            return result
            
        except Exception as e:
            logger.error(f"查询强平订单数据失败: {e}")
            return []
    
    def get_database_info(self):
        """获取数据库信息"""
        try:
            logger.info("获取InfluxDB数据库信息...")
            
            # 获取组织信息
            orgs_api = self.client.organizations_api()
            orgs = orgs_api.find_organizations()
            org_names = [org.name for org in orgs]
            logger.info(f"组织列表: {org_names}")
            
            # 获取存储桶信息 - 修复API调用方式
            try:
                buckets_api = self.client.buckets_api()
                # 使用正确的API调用方式
                buckets = buckets_api.find_buckets()
                if hasattr(buckets, '__iter__'):
                    bucket_names = [bucket.name for bucket in buckets]
                else:
                    # 如果返回的是单个对象，尝试获取名称
                    bucket_names = [buckets.name] if hasattr(buckets, 'name') else []
                logger.info(f"存储桶列表: {bucket_names}")
            except Exception as e:
                logger.warning(f"获取存储桶信息失败: {e}")
                bucket_names = []
            
            # 获取测量信息
            try:
                query = f'''
                import "influxdata/influxdb/schema"
                schema.measurements(bucket: "{self.bucket}")
                '''
                measurements = self.query_api.query(query)
                measurement_list = list(measurements)
                logger.info(f"测量列表: {measurement_list}")
            except Exception as e:
                logger.warning(f"获取测量信息失败: {e}")
                measurement_list = []
            
            return {
                "organizations": org_names,
                "buckets": bucket_names,
                "measurements": measurement_list
            }
            
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            return {}
    
    def close(self):
        """关闭连接"""
        if self.client:
            logger.info("正在关闭InfluxDB连接...")
            self.client.close()
            logger.info("✅ InfluxDB连接已关闭") 