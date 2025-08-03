"""Constants for the StarCharge integration."""

DOMAIN = "starcharge"

# 配置项
CONF_URL = "url"
CONF_METHOD = "method" 
CONF_HEADERS = "headers"

# 默认值
DEFAULT_SCAN_INTERVAL = 15  # 以秒为单位

# API 状态码映射
STATUS_CODES = {
    "00": "空闲",
    "01": "已插枪",
    "02": "正在充电",
}