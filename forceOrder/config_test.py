# 币安强平订单监控系统测试配置

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

# 测试模式配置
TEST_MODE = True

# 模拟InfluxDB配置
INFLUXDB_CONFIG = {
    "url": "http://localhost:8086",
    "token": "test_token",
    "org": "test_org",
    "bucket": "binance_force_orders",
    "measurement": "force_orders"
}

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 