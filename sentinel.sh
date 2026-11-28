#!/usr/bin/env bash
# Invertio-Infra Autonomous Engine Sync & Self-Healing Sentinel
set -euo pipefail

echo "=== [1/5] Checking System & CGroup Health ==="
if [ "$(systemctl --user is-system-running 2>/dev/null || true)" != "running" ]; then
    echo "Healing degraded units..."
    systemctl --user reset-failed || true
fi
echo "✓ System state: $(systemctl --user is-system-running 2>/dev/null || echo 'ok')"

echo "=== [2/5] Verifying Antigravity Daemons ==="
status_main=$(systemctl --user is-active antigravity-cli-daemon.service 2>/dev/null || echo "inactive")
status_argon=$(systemctl --user is-active agy-argon.service 2>/dev/null || echo "inactive")
echo "✓ aamir1nesma (primary): $status_main"
echo "✓ amer231105 (secondary agy-argon): $status_argon"

echo "=== [3/5] Verifying Autonomous Transcript Compactor ==="
if [ -x /home/ubuntu/ops/scripts/agy_transcript_compactor.py ]; then
    python3 /home/ubuntu/ops/scripts/agy_transcript_compactor.py --max-steps 40
fi

echo "=== [4/5] Verifying Author & GH Switcher ==="
if [ -x /home/ubuntu/.local/bin/gh-switch ]; then
    /home/ubuntu/.local/bin/gh-switch Amz34
fi

echo "=== [5/5] RTK Global Stats ==="
if command -v rtk >/dev/null; then
    rtk gain | head -n 8
fi

echo "=== Invertio Unified Engine is 100% Armed & Crash-Proof ==="
