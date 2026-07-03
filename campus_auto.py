#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SRun 校园网自动登录脚本

适用环境：
- Padavan / 老毛子路由器
- Entware Python 3
- 深澜 / SRun 校园网认证系统

注意：
请复制 config.example.py 为 config.py，然后在 config.py 里填写自己的信息。
"""

import base64
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request


try:
    from config import (
        USERNAME,
        PASSWORD,
        PORTAL_HOST,
        AC_ID,
        LOGIN_TYPE,
        N,
        USER_AGENT,
        TEST_HOST,
        REQUEST_TIMEOUT,
    )
except ImportError:
    print("[错误] 找不到 config.py")
    print("请复制 config.example.py 为 config.py，然后填写自己的校园网账号配置。")
    sys.exit(1)


# SRun 前端使用的自定义 Base64 字母表
CUSTOM_B64_ALPHABET = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA"
STANDARD_B64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def log(message):
    """打印带时间的日志。"""
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    print("[{}] {}".format(now, message))


def http_get(url, params=None, timeout=None):
    """发送 GET 请求。"""
    if timeout is None:
        timeout = REQUEST_TIMEOUT

    if params:
        query = urllib.parse.urlencode(params)
        separator = "&" if "?" in url else "?"
        url = url + separator + query

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Referer": "{}/srun_portal_phone?ac_id={}".format(PORTAL_HOST, AC_ID),
        },
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_jsonp(text):
    """
    把 jQuery1124({...}) 这种 JSONP 响应转换成 Python 字典。
    """
    match = re.search(r"^[^(]*\((.*)\)\s*$", text, re.S)

    if not match:
        raise ValueError("无法解析 JSONP 响应：{}".format(text[:200]))

    raw_json = match.group(1)
    return json.loads(raw_json)


def get_ip():
    """
    获取路由器访问校园网认证服务器时使用的真实出口 IP。

    原理：
    执行：
        ip route get 认证服务器IP

    从输出里的 src 提取本机 IP。
    """
    parsed = urllib.parse.urlparse(PORTAL_HOST)
    host = parsed.hostname

    if not host:
        host = PORTAL_HOST.replace("http://", "").replace("https://", "").split("/")[0]

    try:
        output = subprocess.check_output(
            ["ip", "route", "get", host],
            stderr=subprocess.STDOUT,
        ).decode("utf-8", errors="ignore")

        match = re.search(r"\bsrc\s+(\d+\.\d+\.\d+\.\d+)", output)

        if match:
            return match.group(1)

        raise RuntimeError("无法从路由结果中解析 src IP：{}".format(output))

    except Exception as exc:
        raise RuntimeError("获取本机 IP 失败：{}".format(exc))


def get_challenge(ip):
    """向 SRun 服务器获取 challenge token。"""
    url = "{}/cgi-bin/get_challenge".format(PORTAL_HOST)

    params = {
        "callback": "jQuery1124",
        "username": USERNAME,
        "ip": ip,
        "_": str(int(time.time() * 1000)),
    }

    text = http_get(url, params)
    data = extract_jsonp(text)

    if "challenge" not in data:
        raise RuntimeError("服务器没有返回 challenge：{}".format(data))

    return data["challenge"]


def srun_md5(password, token):
    """
    生成 SRun 登录用的 MD5 密码。

    当前这个版本使用：
        md5(password + token)

    如果你的学校返回 auth_info_error，可能需要根据学校前端 JS 调整这里。
    """
    return hashlib.md5((password + token).encode("utf-8")).hexdigest()


def force(message):
    """
    模拟 SRun 前端 JS 的 UTF-8 编码处理。
    """
    result = []

    for char in message:
        n = ord(char)

        if 0x0000 <= n <= 0x007F:
            result.append(char)

        elif 0x0080 <= n <= 0x07FF:
            result.append(chr(0xC0 | ((n >> 6) & 0x1F)))
            result.append(chr(0x80 | (n & 0x3F)))

        elif 0x0800 <= n <= 0xFFFF:
            result.append(chr(0xE0 | ((n >> 12) & 0x0F)))
            result.append(chr(0x80 | ((n >> 6) & 0x3F)))
            result.append(chr(0x80 | (n & 0x3F)))

        elif 0x10000 <= n <= 0x10FFFF:
            result.append(chr(0xF0 | ((n >> 18) & 0x07)))
            result.append(chr(0x80 | ((n >> 12) & 0x3F)))
            result.append(chr(0x80 | ((n >> 6) & 0x3F)))
            result.append(chr(0x80 | (n & 0x3F)))

    return "".join(result)


def ordat(message, index):
    """安全获取字符编码。"""
    if index >= len(message):
        return 0

    return ord(message[index])


def sencode(message, key):
    """
    SRun xEncode 加密算法。

    这个函数用于生成 info 字段。
    """
    message = force(message)
    key = force(key)

    v = []

    for i in range(0, len(message), 4):
        value = (
            ordat(message, i)
            | (ordat(message, i + 1) << 8)
            | (ordat(message, i + 2) << 16)
            | (ordat(message, i + 3) << 24)
        )
        v.append(value)

    k = []

    for i in range(0, len(key), 4):
        value = (
            ordat(key, i)
            | (ordat(key, i + 1) << 8)
            | (ordat(key, i + 2) << 16)
            | (ordat(key, i + 3) << 24)
        )
        k.append(value)

    while len(k) < 4:
        k.append(0)

    n = len(v) - 1
    z = v[n]
    y = v[0]
    c = 0x86014019 | 0x183639A0
    p = 0
    q = int(6 + 52 / (n + 1))
    d = 0

    while q > 0:
        q -= 1
        d = (d + c) & 0xFFFFFFFF
        e = (d >> 2) & 3

        for p in range(n):
            y = v[p + 1]
            m = (
                ((z >> 5) ^ (y << 2))
                + ((y >> 3) ^ (z << 4))
            ) ^ ((d ^ y) + (k[(p & 3) ^ e] ^ z))

            v[p] = (v[p] + m) & 0xFFFFFFFF
            z = v[p]

        y = v[0]
        m = (
            ((z >> 5) ^ (y << 2))
            + ((y >> 3) ^ (z << 4))
        ) ^ ((d ^ y) + (k[(p & 3) ^ e] ^ z))

        v[n] = (v[n] + m) & 0xFFFFFFFF
        z = v[n]

    result = []

    for value in v:
        result.append(chr(value & 0xFF))
        result.append(chr((value >> 8) & 0xFF))
        result.append(chr((value >> 16) & 0xFF))
        result.append(chr((value >> 24) & 0xFF))

    return "".join(result)


def custom_base64_encode(raw_text):
    """
    使用 SRun 自定义字母表进行 Base64 编码。
    """
    raw_bytes = raw_text.encode("latin1")
    standard = base64.b64encode(raw_bytes).decode("ascii")

    table = str.maketrans(STANDARD_B64_ALPHABET, CUSTOM_B64_ALPHABET)
    return standard.translate(table)


def build_info(ip, token):
    """
    构造 info 字段。

    最终格式：
        {SRBX1} + 自定义Base64(xEncode(info_json, token))
    """
    info = {
        "username": USERNAME,
        "password": PASSWORD,
        "ip": ip,
        "acid": AC_ID,
        "enc_ver": "srun_bx1",
    }

    info_json = json.dumps(info, separators=(",", ":"))
    encoded = sencode(info_json, token)

    return "{SRBX1}" + custom_base64_encode(encoded)


def build_chksum(token, ip, hmd5, info):
    """
    构造 chksum 校验字段。
    """
    raw = (
        token + USERNAME
        + token + hmd5
        + token + str(AC_ID)
        + token + ip
        + token + str(N)
        + token + str(LOGIN_TYPE)
        + token + info
    )

    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def login():
    """执行登录流程。"""
    ip = get_ip()
    log("检测到本机 IP：{}".format(ip))

    token = get_challenge(ip)
    log("已获取 challenge token")

    hmd5 = srun_md5(PASSWORD, token)
    info = build_info(ip, token)
    chksum = build_chksum(token, ip, hmd5, info)

    url = "{}/cgi-bin/srun_portal".format(PORTAL_HOST)

    params = {
        "callback": "jQuery1124",
        "action": "login",
        "username": USERNAME,
        "password": "{MD5}" + hmd5,
        "ac_id": str(AC_ID),
        "ip": ip,
        "chksum": chksum,
        "info": info,
        "n": str(N),
        "type": str(LOGIN_TYPE),
        "_": str(int(time.time() * 1000)),
    }

    text = http_get(url, params)

    # 打印原始返回，方便排查
    print(text)

    try:
        data = extract_jsonp(text)
    except Exception:
        return False

    error = data.get("error")
    res = data.get("res")
    suc_msg = data.get("suc_msg")

    if error == "ok" or res == "ok":
        log("登录成功或当前 IP 已在线：{}".format(suc_msg))
        return True

    log("登录失败：{}".format(data))
    return False


def check_network():
    """
    检查外网是否可达。
    这个函数暂时没有在主流程里强制使用，主要给后续扩展用。
    """
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "-W", "2", TEST_HOST],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True

    except Exception:
        return False


def main():
    try:
        success = login()

        if success:
            sys.exit(0)

        sys.exit(2)

    except Exception as exc:
        log("[错误] {}".format(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()