#!/bin/sh

# Padavan 路由器启动后执行示例
# 作用：
# 1. 等待 U 盘挂载
# 2. 如果 /opt 没挂上，就手动补挂
# 3. 再执行校园网自动登录脚本
# 放在Padavan：路由器启动后执行

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