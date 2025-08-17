#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfluxDB数据库状态检查工具
"""

import sys
import os

# 添加forceOrder目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
forceorder_dir = os.path.join(current_dir, 'forceOrder')
sys.path.insert(0, forceorder_dir)

import logging

try:
    from config import INFLUXDB_CONFIG
    logger = logging.getLogger(__name__)
except ImportError as e:
    print(f"❌ 导入配置失败: {e}")
    print(f"当前目录: {current_dir}")
    print(f"forceOrder目录: {forceorder_dir}")
    print(f"Python路径: {sys.path}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_influxdb_connection():
    """检查InfluxDB连接状态"""
    try:
        logger.info("🔍 正在检查InfluxDB连接...")
        
        from influxdb_handler import InfluxDBHandler
        
        # 尝试连接
        handler = InfluxDBHandler()
        
        # 获取数据库信息
        logger.info("📊 获取数据库信息...")
        db_info = handler.get_database_info()
        
        if db_info:
            logger.info("✅ 数据库连接成功！")
            logger.info("📋 数据库信息:")
            logger.info(f"  组织: {db_info.get('organizations', [])}")
            logger.info(f"  存储桶: {db_info.get('buckets', [])}")
            logger.info(f"  测量: {db_info.get('measurements', [])}")
            
            # 检查配置的存储桶是否存在
            target_bucket = INFLUXDB_CONFIG['bucket']
            if target_bucket in db_info.get('buckets', []):
                logger.info(f"✅ 目标存储桶 '{target_bucket}' 存在")
            else:
                logger.warning(f"⚠️ 目标存储桶 '{target_bucket}' 不存在")
                logger.info("请创建存储桶或检查配置")
            
            # 检查配置的组织是否存在
            target_org = INFLUXDB_CONFIG['org']
            if target_org in db_info.get('organizations', []):
                logger.info(f"✅ 目标组织 '{target_org}' 存在")
            else:
                logger.warning(f"⚠️ 目标组织 '{target_org}' 不存在")
                logger.info("请检查组织名称配置")
        
        # 测试写入权限
        logger.info("🧪 测试数据写入权限...")
        test_data = {
            "o": {
                "s": "TESTUSDT",
                "S": "SELL",
                "o": "LIMIT",
                "f": "IOC",
                "q": "1.0",
                "p": "100.0",
                "ap": "100.0",
                "l": "1.0",
                "z": "1.0",
                "X": "FILLED"
            },
            "E": 1234567890000
        }
        
        handler.save_force_order(test_data)
        logger.info("✅ 测试数据写入成功！")
        
        # 测试查询权限
        logger.info("🔍 测试数据查询权限...")
        result = handler.query_recent_force_orders("TESTUSDT", 1)
        if result:
            logger.info("✅ 测试数据查询成功！")
        else:
            logger.warning("⚠️ 测试数据查询失败，可能需要等待数据同步")
        
        handler.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ InfluxDB连接检查失败: {e}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {str(e)}")
        return False

def check_config():
    """检查配置文件"""
    logger.info("📋 检查配置文件...")
    
    logger.info("当前配置:")
    logger.info(f"  InfluxDB URL: {INFLUXDB_CONFIG['url']}")
    logger.info(f"  Token: {INFLUXDB_CONFIG['token'][:10]}...")
    logger.info(f"  组织: {INFLUXDB_CONFIG['org']}")
    logger.info(f"  存储桶: {INFLUXDB_CONFIG['bucket']}")
    logger.info(f"  测量: {INFLUXDB_CONFIG['measurement']}")
    
    # 检查配置完整性
    required_fields = ['url', 'token', 'org', 'bucket', 'measurement']
    missing_fields = []
    
    for field in required_fields:
        if not INFLUXDB_CONFIG.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        logger.error(f"❌ 配置缺失: {missing_fields}")
        return False
    else:
        logger.info("✅ 配置文件完整")
        return True

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 InfluxDB数据库状态检查工具")
    print("=" * 60)
    
    # 检查配置
    config_ok = check_config()
    if not config_ok:
        print("\n❌ 配置检查失败，请修复配置文件")
        return
    
    print("\n" + "=" * 60)
    
    # 检查连接
    connection_ok = check_influxdb_connection()
    
    print("\n" + "=" * 60)
    if connection_ok:
        print("🎉 所有检查通过！InfluxDB配置正确，可以正常使用。")
        print("\n下一步:")
        print("1. 运行监控程序: python forceOrder/main.py")
        print("2. 或使用启动脚本: start_monitor.bat")
    else:
        print("❌ 连接检查失败，请检查以下项目:")
        print("1. InfluxDB服务是否正在运行")
        print("2. 网络连接是否正常")
        print("3. 配置信息是否正确")
        print("4. 访问权限是否足够")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 