# 币安强平订单监控系统

这是一个基于币安U本位合约WebSocket API的强平订单监控系统，支持实时监控SOL、ADA、DOGE、XRP、XLM等币对的强平订单，并将数据存储到InfluxDB数据库中。

## 功能特性

- 🔴 实时监控强平订单数据流
- 📊 支持多币对同时监控（SOL、ADA、DOGE、XRP、XLM）
- 💾 数据自动存储到InfluxDB
- 🔄 自动重连和错误处理
- 📝 详细的日志记录
- 🔍 数据查询和分析工具
- ⚡ 异步处理，高性能
- 🆘 离线模式支持（当InfluxDB不可用时）

## 系统架构

```
币安WebSocket API → WebSocket客户端 → 数据处理 → InfluxDB存储
                                    ↓
                                日志记录 + 离线存储
```

## 安装要求

### 系统要求
- Python 3.8+
- InfluxDB 2.0+
- 网络连接（访问币安API）

### Python依赖
```bash
pip install -r requirements.txt
```

## 配置说明

### 1. 编辑配置文件
修改 `forceOrder/config.py` 文件中的配置：

```python
# InfluxDB配置
INFLUXDB_CONFIG = {
    "url": "http://localhost:8086",        # InfluxDB服务器地址
    "token": "your_influxdb_token_here",   # 你的InfluxDB访问令牌
    "org": "your_org_name",               # 你的组织名称
    "bucket": "binance_force_orders",      # 数据存储桶名称
    "measurement": "force_orders"          # 测量名称
}
```

### 2. 创建InfluxDB存储桶
在InfluxDB中创建名为 `binance_force_orders` 的存储桶。

## 使用方法

### 1. 检查数据库状态
在启动监控系统之前，建议先检查数据库连接状态：

```bash
python check_database.py
```

这个工具会：
- ✅ 检查配置文件完整性
- ✅ 测试InfluxDB连接
- ✅ 验证存储桶和组织权限
- ✅ 测试数据写入和查询功能

### 2. 启动监控系统
```bash
cd forceOrder
python main.py
```

### 3. 使用查询工具
```bash
python forceOrder/query_tool.py
```

查询工具提供以下功能：
- 查询指定币对的强平订单
- 查询所有币对的强平订单统计
- 查询强平订单汇总信息
- 查看数据摘要

### 4. 查看日志
系统运行时会生成 `force_order_monitor.log` 日志文件，记录所有操作和错误信息。

## 日志说明

### 日志级别
系统提供详细的日志记录，包括：

- 🚀 **启动信息**: 系统启动、组件初始化
- 📊 **数据库信息**: 连接状态、存储桶信息、权限验证
- 🎯 **数据接收**: 强平订单数据接收和处理
- 💾 **数据存储**: 数据写入InfluxDB的详细过程
- ✅ **操作成功**: 各种操作的成功确认
- ❌ **错误信息**: 详细的错误类型和描述
- 🔄 **状态变化**: 连接状态、模式切换等

### 关键日志标识
- ✅ 成功操作
- ❌ 错误操作
- ⚠️ 警告信息
- 🔍 检查/验证操作
- 💾 数据存储操作
- 🌐 网络连接操作

## 数据字段说明

根据币安API文档，强平订单数据包含以下字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| `s` | 交易对 | "SOLUSDT" |
| `S` | 订单方向 | "SELL" / "BUY" |
| `o` | 订单类型 | "LIMIT" |
| `f` | 有效方式 | "IOC" |
| `q` | 订单数量 | "0.014" |
| `p` | 订单价格 | "9910" |
| `ap` | 平均价格 | "9910" |
| `X` | 订单状态 | "FILLED" |
| `l` | 最近成交量 | "0.014" |
| `z` | 累计成交量 | "0.014" |
| `T` | 交易时间 | 1568014460893 |

## 监控的币对

系统默认监控以下币对：
- **SOLUSDT** - Solana
- **ADAUSDT** - Cardano  
- **DOGEUSDT** - Dogecoin
- **XRPUSDT** - Ripple
- **XLMUSDT** - Stellar

## 数据存储结构

数据以时间序列形式存储在InfluxDB中：

- **Measurement**: `force_orders`
- **Tags**: `symbol`, `side`, `order_type`, `time_in_force`, `status`
- **Fields**: `quantity`, `price`, `avg_price`, `last_qty`, `cum_qty`
- **Timestamp**: 事件时间

## 故障排除

### 常见问题

1. **连接失败**
   - 运行 `python check_database.py` 检查连接状态
   - 检查网络连接
   - 验证InfluxDB配置
   - 确认币安API可访问

2. **数据不更新**
   - 检查WebSocket连接状态
   - 查看日志文件中的错误信息
   - 确认币对配置正确
   - 检查是否有强平订单发生

3. **InfluxDB错误**
   - 验证数据库连接信息
   - 检查存储桶权限
   - 确认组织名称正确
   - 查看详细错误日志

4. **离线模式**
   - 当InfluxDB不可用时，系统自动切换到离线模式
   - 数据保存在 `force_orders_data.json` 文件中
   - 可以稍后导入到InfluxDB

### 日志级别
可以通过修改 `config.py` 中的 `LOG_LEVEL` 来调整日志详细程度：
- `DEBUG`: 详细调试信息
- `INFO`: 一般信息（推荐）
- `WARNING`: 警告信息
- `ERROR`: 错误信息

## 开发说明

### 项目结构
```
forceOrder/
├── config.py              # 配置文件
├── config.example.py      # 配置模板
├── influxdb_handler.py    # InfluxDB客户端
├── websocket_client.py    # WebSocket客户端
├── data_processor.py      # 离线数据处理器
├── main.py               # 主程序
├── query_tool.py         # 查询工具
└── common.py             # 公共模块
```

### 扩展功能
- 添加更多币对监控
- 实现数据导出功能
- 添加Web界面
- 集成告警系统
- 数据分析报表

## 许可证

本项目采用MIT许可证。

## 免责声明

本系统仅用于学习和研究目的，不构成投资建议。使用本系统进行交易决策的风险由用户自行承担。

## 技术支持

如有问题或建议，请提交Issue或联系开发者。

---

**注意**: 使用前请确保已正确配置InfluxDB，并具有相应的访问权限。 