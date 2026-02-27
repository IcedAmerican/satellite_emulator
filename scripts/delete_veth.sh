#!/bin/bash
# 删除 LEO 链/卫星仿真创建的 veth 接口（cn*_index*）
# 用法: sudo ./delete_veth.sh [--host-only] [--containers-only] [--yes]

set -e

HOST_ONLY=false
CONTAINERS_ONLY=false
YES=false

for arg in "$@"; do
  case "$arg" in
    --host-only)     HOST_ONLY=true ;;
    --containers-only) CONTAINERS_ONLY=true ;;
    --yes|-y)        YES=true ;;
    -h|--help)
      echo "用法: $0 [选项]"
      echo "  默认: 先清主机上的 veth，再清运行中容器内的 veth"
      echo "  --host-only       只清理主机上的 veth"
      echo "  --containers-only 只清理容器内的 veth"
      echo "  --yes, -y         不确认直接执行"
      exit 0
      ;;
  esac
done

if [ "$(id -u)" -ne 0 ]; then
  echo "请使用 sudo 运行: sudo $0 $*"
  exit 1
fi

# 主机上的 veth（匹配 cn数字_index数字）
# ip link show 显示为 "A@B"，但 ip link delete 需用设备名 A（@ 前半段），与 delete.sh 一致
clean_host_veth() {
  local count=0
  local stuck=0
  while true; do
    local full_name
    full_name=$(ip -o link show type veth 2>/dev/null | awk -F': ' '/cn[0-9]+_index[0-9]+/ {gsub(/:.*/, "", $2); print $2; exit}' || true)
    [ -z "$full_name" ] && break
    # 删除时只用 @ 前的设备名（如 cn10_index1@cn6_index4 -> cn10_index1）
    local dev_name="${full_name%%@*}"
    echo "  删除主机接口: $dev_name ($full_name)"
    if ip link delete "$dev_name" 2>&1; then
      count=$((count + 1))
      stuck=0
    elif ip link delete "$full_name" 2>&1; then
      count=$((count + 1))
      stuck=0
    elif command -v nsenter >/dev/null 2>&1 && nsenter -t 1 -n ip link delete "$dev_name" 2>&1; then
      count=$((count + 1))
      stuck=0
    else
      echo "  删除失败，请检查权限或网络命名空间"
      stuck=$((stuck + 1))
      [ "$stuck" -ge 3 ] && break
    fi
  done
  echo "  主机共删除 $count 个 veth"
}

# 容器内的 veth
clean_container_veth() {
  local cids
  cids=$(docker ps -q --filter "name=consensus_node" 2>/dev/null || true)
  if [ -z "$cids" ]; then
    echo "  没有运行中的 consensus_node 容器，跳过容器内清理"
    return
  fi
  local count=0
  for cid in $cids; do
    local name
    name=$(docker inspect -f '{{.Name}}' "$cid" 2>/dev/null | sed 's/^\///')
    while read -r iface; do
      [ -z "$iface" ] && continue
      echo "  容器 $name 删除: $iface"
      docker exec "$cid" ip link delete "$iface" 2>/dev/null || true
      count=$((count + 1))
    done < <(docker exec "$cid" ip -o link show type veth 2>/dev/null | awk -F': ' '{print $2}' | grep -E '^cn[0-9]+_index[0-9]+' || true)
  done
  echo "  容器内共删除 $count 个 veth"
}

run_clean() {
  if [ "$HOST_ONLY" = true ]; then
    echo "=== 仅清理主机 veth ==="
    clean_host_veth
    return
  fi
  if [ "$CONTAINERS_ONLY" = true ]; then
    echo "=== 仅清理容器内 veth ==="
    clean_container_veth
    return
  fi
  echo "=== 清理主机 veth ==="
  clean_host_veth
  echo "=== 清理容器内 veth ==="
  clean_container_veth
}

echo "将删除所有符合 cn*_index* 的 veth 接口（主机 + 运行中共识节点容器内）。"
if [ "$YES" != true ]; then
  read -r -p "继续? [y/N] " r
  case "$r" in
    [yY]|[yY][eE][sS]) ;;
    *) echo "已取消"; exit 0 ;;
  esac
fi

run_clean
echo "完成。"
