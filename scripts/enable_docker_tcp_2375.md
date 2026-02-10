# 开放 Docker 2375 端口

Docker 默认只监听 Unix 套接字。要让本机或远程通过 `http://IP:2375` 访问 Docker API，需要让 dockerd 同时监听 TCP 2375。

## 方法一：用 systemd 覆盖（推荐）

1. 创建覆盖目录并编辑配置：

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/listen-tcp.conf << 'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375
EOF
```

2. 重载并重启 Docker：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

3. 检查是否在监听 2375：

```bash
ss -tlnp | grep 2375
# 或
sudo netstat -tlnp | grep 2375
```

## 方法二：仅本机访问（更安全）

若只需本机访问（如 `base_url: http://127.0.0.1:2375`），可只监听 127.0.0.1：

```bash
sudo tee /etc/systemd/system/docker.service.d/listen-tcp.conf << 'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// -H tcp://127.0.0.1:2375
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 安全提示

- **2375 为明文端口**，无认证、无加密，仅适合内网或开发环境。
- 对公网或不可信网络请使用 **2376 + TLS** 并做访问控制。
- 若本机有多网卡，监听 `0.0.0.0:2375` 表示所有网卡都可访问，请确保防火墙只放行可信 IP。

## 与 constellation_config 的关系

`resources/constellation_config.yml` 中 `base_url` 需与上述监听方式一致：

- 仅本机：`base_url: http://127.0.0.1:2375`
- 内网其他机器访问：`base_url: http://本机IP:2375`，且需用方法一监听 `0.0.0.0:2375`。
