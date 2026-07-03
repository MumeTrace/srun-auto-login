#!/bin/sh

# Padavan WAN 上线后执行示例
# 作用：
# 1. WAN 网络恢复后，等待一段时间
# 2. 检查 /opt 是否挂载
# 3. 执行校园网自动登录脚本
# 放在Padavan：WAN 上行 / 下行启动后执行

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