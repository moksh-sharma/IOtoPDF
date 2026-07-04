#!/usr/bin/env bash
# Oracle Cloud Always Free VM - one-time setup for IOtoPDF
# Run on Ubuntu 22.04/24.04 after SSH: bash scripts/oracle-vm-setup.sh

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/moksh-sharma/IOtoPDF.git}"
APP_DIR="${APP_DIR:-$HOME/IOtoPDF}"

echo "==> Updating system..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

echo "==> Installing Docker..."
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
fi

echo "==> Opening ports in iptables (Oracle requires this in addition to Security List)..."
sudo iptables -C INPUT -p tcp --dport 22 -j ACCEPT 2>/dev/null || \
  sudo iptables -I INPUT 5 -m state --state NEW -p tcp --dport 22 -j ACCEPT
sudo iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || \
  sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -C INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || \
  sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT

if command -v netfilter-persistent >/dev/null 2>&1; then
  sudo netfilter-persistent save
elif apt-get install -y iptables-persistent 2>/dev/null; then
  sudo netfilter-persistent save
fi

echo "==> Cloning app..."
if [ -d "$APP_DIR/.git" ]; then
  cd "$APP_DIR" && git pull
else
  git clone "$REPO_URL" "$APP_DIR"
  cd "$APP_DIR"
fi

echo "==> Building and starting..."
sudo docker compose up -d --build

PUBLIC_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "YOUR_VM_PUBLIC_IP")

echo ""
echo "============================================"
echo "  IOtoPDF is running!"
echo "  Open: http://${PUBLIC_IP}"
echo "============================================"
echo ""
echo "Useful commands:"
echo "  cd $APP_DIR"
echo "  sudo docker compose logs -f    # view logs"
echo "  sudo docker compose restart  # restart app"
echo "  git pull && sudo docker compose up -d --build  # update app"
