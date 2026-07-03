# 常见问题排查

## 1. 报错：/opt/bin/python3: not found

说明 `/opt` 没有挂载成功。

先检查：

```sh
df -h
mount | grep opt
ls /opt/bin
```

如果看到 U 盘挂载在：

```text
/media/AiDisk_a1
```

但是没有 `/opt/bin`，说明系统没有把：

```text
/media/AiDisk_a1/opt
```

映射到：

```text
/opt
```

可以手动修复：

```sh
mkdir -p /opt
mount --bind /media/AiDisk_a1/opt /opt
```

然后测试：

```sh
/opt/bin/python3 --version
/opt/bin/python3 /opt/bin/campus_auto.py
```

---

## 2. 返回 ip_already_online_error

这不是失败。

意思是：

```text
当前 IP 已经在线
```

只要返回里有：

```text
"error":"ok"
"res":"ok"
```

就说明认证状态正常。

---

## 3. 返回 auth_info_error

通常说明加密参数不匹配。

重点检查：

- 账号是否正确
- 密码是否正确
- ac_id 是否正确
- 认证服务器地址是否正确
- 本机 IP 获取是否正确
- md5 算法是否和学校前端一致
- xEncode 是否和学校前端一致
- Base64 自定义字母表是否一致

---

## 4. 没有日志文件

日志文件只有在你这样运行后才会生成：

```sh
/opt/bin/python3 /opt/bin/campus_auto.py >> /opt/campus_auto.log 2>&1
```

如果直接运行：

```sh
/opt/bin/python3 /opt/bin/campus_auto.py
```

那么结果会直接显示在终端，不会写入日志。

---

## 5. U 盘识别了，但是 /opt 没有

如果：

```sh
df -h
```

显示：

```text
/dev/sda1  /media/AiDisk_a1
```

但是：

```sh
ls /opt/bin
```

提示不存在，说明 Padavan 的自动 opt 映射失败。

可以在启动脚本里加：

```sh
mkdir -p /opt

mount | grep " on /opt " >/dev/null 2>&1
if [ $? -ne 0 ]; then
  mount --bind /media/AiDisk_a1/opt /opt
fi
```

这样就算系统忘了挂 `/opt`，脚本也会自己补挂。