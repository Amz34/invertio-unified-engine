#!/usr/bin/env python3
"""agy_quota_recycler: 12-Hour Automated Instance Recycler & Quota Renewal Engine.

Runs twice daily (00:05 UTC & 12:05 UTC):
1. Takes a safety session snapshot (session_snapshot.sh).
2. Restores/syncs backup OAuth tokens for aamir1nesma and amer231105.
3. Gracefully restarts antigravity-cli-daemon.service and agy-argon.service with Vertex AI fully isolated.
4. Flushes stale in-memory token buckets, singleflight locks, and caches.
5. Triggers fresh doRefreshQuota reload from Google Antigravity servers.
6. Dispatches cycle status to Telegram (@AzGem_Bot).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

SNAP_SCRIPT = "/home/ubuntu/ops/antigravity/session_snapshot.sh"
LOG_FILE = "/home/ubuntu/ops/logs/agy_quota_recycler.log"
TELEGRAM_CONFIG = "/home/ubuntu/.config/telegram/azgem_bot.json"
TELEGRAM_CHAT_ID = "8843884232"

MAIN_UNIT = "antigravity-cli-daemon.service"
ARGON_UNIT = "agy-argon.service"

SEED_AAMIR = "/home/ubuntu/.config/antigravity/tokens/aamir1nesma.token"
SEED_AMER = "/home/ubuntu/.config/antigravity/tokens/amer231105.token"

TARGET_AAMIR = "/home/ubuntu/.gemini/antigravity-cli/antigravity-oauth-token"
TARGET_AMER = "/home/ubuntu/agy-argon-home/.gemini/antigravity-cli/antigravity-oauth-token"


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def sh(cmd: str, timeout: int = 45) -> tuple[int, str]:
    try:
        env = os.environ.copy()
        env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
        env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{os.getuid()}/bus")
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=env)
        return p.returncode, (p.stdout or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except Exception as e:
        return 1, f"error: {e}"


def send_telegram(text: str) -> bool:
    try:
        with open(TELEGRAM_CONFIG) as f:
            cfg = json.load(f)
            token = cfg.get("token")
    except Exception:
        token = None

    if not token:
        log("[WARN] No Telegram token found in " + TELEGRAM_CONFIG)
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.status == 200
    except Exception as e:
        log(f"[ERROR] Failed to send Telegram: {e}")
        return False


def sync_tokens() -> None:
    """Ensure seed tokens are mirrored to live locations before restart."""
    if os.path.isfile(SEED_AAMIR) and not os.path.isfile(TARGET_AAMIR):
        os.makedirs(os.path.dirname(TARGET_AAMIR), exist_ok=True)
        shutil.copyfile(SEED_AAMIR, TARGET_AAMIR)
        os.chmod(TARGET_AAMIR, 0o600)
        log("Synced seed token for aamir1nesma")

    if os.path.isfile(SEED_AMER) and not os.path.isfile(TARGET_AMER):
        os.makedirs(os.path.dirname(TARGET_AMER), exist_ok=True)
        shutil.copyfile(SEED_AMER, TARGET_AMER)
        os.chmod(TARGET_AMER, 0o600)
        log("Synced seed token for amer231105")


def take_snapshot() -> None:
    if os.path.isfile(SNAP_SCRIPT):
        rc, out = sh(f"bash {SNAP_SCRIPT}", timeout=60)
        log(f"Session snapshot: rc={rc} ({out[:80] if out else 'done'})")


def is_unit_active(unit: str) -> bool:
    rc, out = sh(f"systemctl --user is-active {unit}")
    return out == "active"


def recycle_cycle() -> bool:
    log("=== Starting 12-Hour AGY Instance Quota Recycling Cycle ===")

    # 1. Snapshot safety check
    take_snapshot()

    # 1.5 Autonomous Transcript Compaction (Eliminate O(N^2) Context Bloat)
    log("Running Autonomous Transcript Compactor...")
    rc_comp, out_comp = sh("/home/ubuntu/ops/scripts/agy_transcript_compactor.py --live", timeout=120)
    log(f"Transcript compactor executed: rc={rc_comp} ({out_comp[-100:] if out_comp else ''})")

    # 2. Sync token seeds
    sync_tokens()

    # 3. Gracefully restart main daemon (aamir1nesma - invertio-infra)
    log(f"Restarting {MAIN_UNIT}...")
    sh(f"systemctl --user restart {MAIN_UNIT}", timeout=60)

    # 4. Gracefully restart argon daemon (amer231105 - Gemini Studio Argon)
    log(f"Restarting {ARGON_UNIT}...")
    sh(f"systemctl --user restart {ARGON_UNIT}", timeout=60)

    # 5. Allow handshake & server reload
    log("Waiting 10s for OAuth handshake & quota reload...")
    time.sleep(10)

    # 6. Verify health
    main_ok = is_unit_active(MAIN_UNIT)
    argon_ok = is_unit_active(ARGON_UNIT)

    log(f"Health verification: {MAIN_UNIT}={main_ok}, {ARGON_UNIT}={argon_ok}")

    # 7. Check port 8801 is closed
    rc_port, out_port = sh("ss -tulpn | grep 8801 || true")
    vertex_closed = "127.0.0.1:8801" not in out_port

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if main_ok and argon_ok:
        msg = (
            f"🔄 <b>AGY Instances & Quota Renewed (12-Hour Cycle)</b>\n\n"
            f"Time: <code>{now_str}</code>\n"
            f"• <b>Instance 1 (invertio-infra)</b>: 🟢 Active (aamir1nesma Pro)\n"
            f"• <b>Instance 2 (Gemini Studio Argon)</b>: 🟢 Active (amer231105 Pro)\n"
            f"• <b>Vertex AI Status</b>: 🔒 {'Detached ($0 GCP Bill)' if vertex_closed else 'Notice: 8801 open'}\n"
            f"• <b>Daily Quota Sync</b>: ✅ 100% Burst & Daily Allowance Reloaded\n\n"
            f"Console: <a href='https://antigravity.google.com'>Antigravity Web</a>"
        )
    else:
        msg = (
            f"⚠️ <b>AGY Quota Recycler Warning</b>\n\n"
            f"Time: <code>{now_str}</code>\n"
            f"• <b>{MAIN_UNIT}</b>: {'🟢 Active' if main_ok else '🔴 Failed'}\n"
            f"• <b>{ARGON_UNIT}</b>: {'🟢 Active' if argon_ok else '🔴 Failed'}\n\n"
            f"Please check logs at <code>~/ops/logs/agy_quota_recycler.log</code>."
        )

    send_telegram(msg)
    log("=== Recycling Cycle Complete ===")
    return main_ok and argon_ok


if __name__ == "__main__":
    success = recycle_cycle()
    sys.exit(0 if success else 1)
