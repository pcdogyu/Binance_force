# 币安强平订单监控系统配置

# 币安WebSocket配置
BINANCE_WS_BASE_URL = "wss://fstream.binance.com/ws"

# 监控模式选择
MONITOR_MODE = "all_market"  # "all_market" 或 "specific_symbols"

# 监控的币对列表 (仅在 specific_symbols 模式下使用)
SYMBOLS = [
    "SOLUSDT",
    "ADAUSDT", 
    "DOGEUSDT",
    "XRPUSDT",
    "XLMUSDT"
]

# 全市场强平订单流名称
ALL_MARKET_STREAM = "!forceOrder@arr"

# InfluxDB配置
INFLUXDB_CONFIG = {
    "url": "http://localhost:8086",
    "token": "admin:admin123",  # 用户名:密码格式
    "org": "myorg",             # 实际的组织名称
    "bucket": "binance_force_orders",
    "measurement": "force_orders"
}

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 