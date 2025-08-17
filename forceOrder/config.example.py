# 币安强平订单监控系统配置模板
# 请复制此文件为 config.py 并修改相应配置

# 币安WebSocket配置
BINANCE_WS_BASE_URL = "wss://fstream.binance.com/ws"

# 监控的币对列表
SYMBOLS = [
    "SOLUSDT",
    "ADAUSDT", 
    "DOGEUSDT",
    "XRPUSDT",
    "XLMUSDT"
]

# InfluxDB配置 - 请根据你的环境修改
INFLUXDB_CONFIG = {
    "url": "http://localhost:8086",           # InfluxDB服务器地址
    "token": "your_influxdb_token_here",      # 你的InfluxDB访问令牌
    "org": "your_org_name",                  # 你的组织名称
    "bucket": "binance_force_orders",         # 数据存储桶名称
    "measurement": "force_orders"             # 测量名称
}

# 日志配置
LOG_LEVEL = "INFO"  # 可选: DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 示例InfluxDB配置说明:
# 1. 在InfluxDB中创建组织(Organization)
# 2. 创建存储桶(Bucket)名为 "binance_force_orders"
# 3. 生成访问令牌(Token)并确保有读写权限
# 4. 将上述信息填入对应字段 