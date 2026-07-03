# SRun 校园网自动登录脚本

这是一个适用于 Padavan / 老毛子路由器 + Entware Python 的 SRun/深澜 校园网自动登录脚本。

本项目只用于自动登录自己的校园网账号，不用于绕过认证、不用于冒用他人账号、不用于攻击校园网系统。

---

## 功能

- 自动获取 SRun challenge token
- 自动生成登录用 MD5 密码
- 自动生成 `{SRBX1}` 加密 info 字段
- 自动生成 chksum 校验字段
- 自动提交登录请求
- 支持 Padavan 启动脚本
- 支持定时任务自动重连

---

## 适用环境

已测试环境：

- Padavan / 老毛子路由器
- Entware Python 3
- SRun 深澜认证系统
- 认证服务版本示例：`SRunCGIAuthIntfSvr V1.18`

---

## 安装 Python

在路由器 SSH 里执行：

```sh
opkg update
opkg install python3-light python3-codecs python3-urllib
```

确认：

```sh
/opt/bin/python3 --version
```

---

## 安装脚本

把文件复制到路由器：

```sh
cp campus_auto.py /opt/bin/campus_auto.py
cp config.example.py /opt/bin/config.py
chmod +x /opt/bin/campus_auto.py
```

编辑配置：

```sh
vi /opt/bin/config.py
```

填写：

```python
USERNAME = "你的账号"
PASSWORD = "你的密码"
PORTAL_HOST = "http://你的认证服务器地址"
AC_ID = "4"
```

---

## 手动测试

```sh
/opt/bin/python3 /opt/bin/campus_auto.py
```

成功返回通常包含：

```text
"error":"ok"
"res":"ok"
"suc_msg":"login_ok"
```

如果返回：

```text
"suc_msg":"ip_already_online_error"
```

也说明正常，意思是当前 IP 已经在线。

---

## Padavan 启动脚本

放到：

```text
高级设置 -> 系统管理 -> 服务 -> 自定义脚本 -> 路由器启动后执行
```

示例：

```sh
(
  sleep 60

  mkdir -p /opt

  mount | grep " on /opt " >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    mount --bind /media/AiDisk_a1/opt /opt
  fi

  sleep 120

  /opt/bin/python3 /opt/bin/campus_auto.py >> /opt/campus_auto.log 2>&1
)&
```

---

## WAN 上线后执行

放到：

```text
高级设置 -> 系统管理 -> 服务 -> 自定义脚本 -> WAN 上行 / 下行启动后执行
```

示例：

```sh
(
  sleep 60

  mkdir -p /opt

  mount | grep " on /opt " >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    mount --bind /media/AiDisk_a1/opt /opt
  fi

  sleep 120

  /opt/bin/python3 /opt/bin/campus_auto.py >> /opt/campus_auto.log 2>&1
)&
```

---

## 定时任务

添加定时任务：

```sh
cru.sh a campus_7 "0 7 * * * /opt/bin/python3 /opt/bin/campus_auto.py >> /opt/campus_auto.log 2>&1"

cru.sh a campus_705 "5 7 * * * /opt/bin/python3 /opt/bin/campus_auto.py >> /opt/campus_auto.log 2>&1"

cru.sh a campus_710 "10 7 * * * /opt/bin/python3 /opt/bin/campus_auto.py >> /opt/campus_auto.log 2>&1"

cru.sh a campus_check "*/10 * * * * ping -c 1 223.5.5.5 >/dev/null || /opt/bin/python3 /opt/bin/campus_auto.py >> /opt/campus_auto.log 2>&1"
```

查看：

```sh
crontab -l
```

---

## 许可证

MIT