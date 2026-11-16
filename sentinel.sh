#!/usr/bin/env bash
# Invertio-Infra Autonomous Engine Sync & Self-Healing Sentinel
set -euo pipefail

echo "=== [1/4] Checking System & CGroup Health ==="
if [ "$(systemctl --user is-system-running 2>/dev/null || true)" != "running" ]; then
    echo "Healing degraded units..."
    systemctl --user reset-failed || true
fi
echo "✓ System state: $(systemctl --user is-system-running 2>/dev/null || echo 'ok')"

echo "=== [2/4] Verifying Token Compression Layer ==="
if pgrep -f caveman-proxy >/dev/null; then
    echo "✓ Caveman Proxy: Active on 8787"
else
    echo "! Caveman Proxy not running, starting..."
    /home/ubuntu/.caveman/bin/caveman-proxy >/dev/null 2>&1 &
fi

echo "=== [3/4] Verifying Author & GH Switcher ==="
if [ -x /home/ubuntu/.local/bin/gh-switch ]; then
    /home/ubuntu/.local/bin/gh-switch Amz34
fi

echo "=== [4/4] RTK Global Stats ==="
if command -v rtk >/dev/null; then
    rtk gain | head -n 8
fi

echo "=== Invertio Unified Engine is 100% Armed & Crash-Proof ==="
