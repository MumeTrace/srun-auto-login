# -*- coding: utf-8 -*-

"""
配置文件示例。

使用方法：
1. 复制本文件为 config.py
2. 修改 config.py 里的账号、密码、认证地址
"""

# 校园网账号
USERNAME = "你的账号"

# 校园网密码
PASSWORD = "你的密码"

# 校园网认证服务器地址
# 示例：
# PORTAL_HOST = "http://10.110.74.91"
PORTAL_HOST = "http://你的认证服务器地址"

# ac_id 通常来自认证页面地址：
# srun_portal_phone?ac_id=4
AC_ID = "4"

# SRun 登录固定参数
LOGIN_TYPE = "1"
N = "200"

# 请求头
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# 用于检测外网是否可达
TEST_HOST = "223.5.5.5"

# 请求超时时间，单位：秒
REQUEST_TIMEOUT = 8